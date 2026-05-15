import json
import logging
import time
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Page, BrowserContext

logger = logging.getLogger(__name__)

SESSION_FILE = Path(__file__).parent / ".session.json"
BASE_URL = "https://higgsfield.ai"
LOGIN_URL = f"{BASE_URL}/auth/email/sign-in"
VIDEO_URL = f"{BASE_URL}/create/video?model=seedance_2_0"


class HiggsFieldScraper:
    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        cookies_json: Optional[str] = None,
    ):
        self.email = email
        self.password = password
        self.cookies_json = cookies_json

    # ── Browser setup ────────────────────────────────────────────────────────

    def _make_context(self, playwright):
        browser = playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        ctx_kwargs: dict = {
            "viewport": {"width": 1400, "height": 900},
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }
        if SESSION_FILE.exists():
            ctx_kwargs["storage_state"] = str(SESSION_FILE)

        context = browser.new_context(**ctx_kwargs)

        if self.cookies_json:
            try:
                raw = self.cookies_json.strip()
                if raw.startswith("["):
                    cookies = json.loads(raw)
                else:
                    cookies = [
                        {
                            "name": p.split("=", 1)[0].strip(),
                            "value": p.split("=", 1)[1].strip() if "=" in p else "",
                            "domain": "higgsfield.ai",
                            "path": "/",
                        }
                        for p in raw.split(";")
                        if "=" in p
                    ]
                context.add_cookies(cookies)
            except Exception as exc:
                logger.warning("Could not parse HIGGSFIELD_COOKIES: %s", exc)

        return browser, context

    # ── Auth ────────────────────────────────────────────────────────────────

    def _is_logged_in(self, page: Page) -> bool:
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15_000)
        except Exception:
            pass
        return "/auth" not in page.url and "/login" not in page.url

    def _login(self, page: Page) -> None:
        if not (self.email and self.password):
            raise RuntimeError(
                "Not authenticated. Set HIGGSFIELD_EMAIL + HIGGSFIELD_PASSWORD in .env, "
                "or export your browser cookies as HIGGSFIELD_COOKIES.\n"
                "See README.md for cookie extraction instructions."
            )
        logger.info("Logging in as %s …", self.email)
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30_000)
        page.locator('input[type="email"]').first.fill(self.email)
        page.locator('input[type="password"]').first.fill(self.password)
        page.locator('button[type="submit"]').first.click()
        # Wait until URL leaves /auth
        page.wait_for_url(
            lambda url: "/auth" not in url,
            timeout=25_000,
        )
        logger.info("Login successful.")

    # ── Image upload ────────────────────────────────────────────────────────

    def _upload_image(self, page: Page, image_path: str) -> None:
        logger.info("Uploading image %s …", image_path)
        # Some pages expose a visible file input
        fi = page.locator('input[type="file"]').first
        if fi.count() and fi.is_visible():
            fi.set_input_files(image_path)
            time.sleep(1.5)
            return

        # Otherwise find and click a media-add button, then handle the file chooser
        upload_triggers = [
            '[aria-label*="upload" i]',
            '[aria-label*="image" i]',
            'button:has-text("Add")',
            'button:has-text("Upload")',
            '[data-testid*="upload"]',
            'label[for*="file"]',
        ]
        for sel in upload_triggers:
            btn = page.locator(sel).first
            if btn.count() and btn.is_visible():
                with page.expect_file_chooser() as fc_info:
                    btn.click()
                fc_info.value.set_files(image_path)
                time.sleep(1.5)
                logger.info("Image uploaded via %s.", sel)
                return

        # Last resort: force-set the hidden file input
        fi_hidden = page.locator('input[type="file"]').first
        if fi_hidden.count():
            fi_hidden.set_input_files(image_path)
            time.sleep(1.5)
            return

        logger.warning("No upload target found — skipping image upload.")

    # ── Prompt ──────────────────────────────────────────────────────────────

    def _fill_prompt(self, page: Page, text: str) -> None:
        editor = page.locator("[data-lexical-editor]").first
        if not editor.count():
            raise RuntimeError(
                "Prompt editor not found. The page layout may have changed."
            )
        # Clear existing content via JS (Lexical ignores direct value manipulation)
        page.evaluate("""() => {
            const el = document.querySelector('[data-lexical-editor]');
            if (!el) return;
            el.focus();
            document.execCommand('selectAll', false, null);
            document.execCommand('delete', false, null);
        }""")
        time.sleep(0.2)
        editor.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        page.keyboard.type(text, delay=18)
        logger.info("Prompt typed.")

    # ── Generate ────────────────────────────────────────────────────────────

    def _click_generate(self, page: Page) -> None:
        # Try multiple selector strategies
        candidates = [
            page.locator("button").filter(has_text="Generate").first,
            page.get_by_role("button", name="Generate"),
            page.locator('[data-testid*="generate"]').first,
        ]
        for btn in candidates:
            try:
                if btn.count() and btn.is_visible() and btn.is_enabled():
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    logger.info("Generate clicked.")
                    return
            except Exception:
                continue
        raise RuntimeError(
            "Generate button not found. Higgsfield UI may have changed."
        )

    # ── Wait for video ───────────────────────────────────────────────────────

    def _wait_for_video(
        self, page: Page, captured: list[str], timeout_s: int = 360
    ) -> str:
        logger.info("Waiting for video (up to %ds) …", timeout_s)
        deadline = time.time() + timeout_s

        while time.time() < deadline:
            # 1. Network-intercepted MP4 URLs (most reliable)
            mp4s = [u for u in captured if ".mp4" in u and "http" in u]
            if mp4s:
                logger.info("Found video via network: %s", mp4s[-1])
                return mp4s[-1]

            # 2. video element in the DOM
            url: Optional[str] = page.evaluate("""() => {
                for (const v of document.querySelectorAll('video')) {
                    if (v.src && v.src.startsWith('http')) return v.src;
                    const src = v.querySelector('source[src]');
                    if (src && src.src.startsWith('http')) return src.src;
                }
                for (const a of document.querySelectorAll('a[href*=".mp4"], a[download]')) {
                    if (a.href && a.href.startsWith('http')) return a.href;
                }
                return null;
            }""")
            if url:
                logger.info("Found video in DOM: %s", url)
                return url

            # 3. Any captured video-like URL as fallback
            if captured:
                logger.info("Using last captured URL: %s", captured[-1])
                return captured[-1]

            time.sleep(3)

        raise TimeoutError(
            f"Video was not ready after {timeout_s}s. "
            "Generation may still be running on Higgsfield — try again."
        )

    # ── Main entrypoint ──────────────────────────────────────────────────────

    def generate(self, prompt: str, image_path: Optional[str] = None) -> str:
        """Login if needed, submit prompt (+image), return the generated video URL."""
        captured_urls: list[str] = []

        with sync_playwright() as p:
            browser, context = self._make_context(p)
            page = context.new_page()

            def on_response(response):
                url = response.url
                ct = response.headers.get("content-type", "")
                if "video" in ct or any(ext in url for ext in (".mp4", ".webm", ".m3u8")):
                    captured_urls.append(url)

            page.on("response", on_response)

            try:
                page.goto(VIDEO_URL, wait_until="domcontentloaded", timeout=60_000)

                if not self._is_logged_in(page):
                    self._login(page)
                    context.storage_state(path=str(SESSION_FILE))
                    page.goto(VIDEO_URL, wait_until="domcontentloaded", timeout=60_000)

                page.wait_for_load_state("networkidle", timeout=30_000)

                if image_path:
                    self._upload_image(page, image_path)

                self._fill_prompt(page, prompt)
                self._click_generate(page)

                video_url = self._wait_for_video(page, captured_urls)

                # Persist session so next run skips login
                context.storage_state(path=str(SESSION_FILE))
                return video_url

            finally:
                browser.close()
