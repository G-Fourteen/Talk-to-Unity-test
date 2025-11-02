import pytest
from playwright.sync_api import sync_playwright


SITE_URL = "http://www.unityailab.com/Talk-to-Unity/"


STUB_SCRIPT = """
(() => {
    const state = {
        speakCalls: [],
        recognitionStartCalls: 0,
        recognitionStopCalls: 0,
        getUserMediaCalls: 0
    };

    Object.defineProperty(window, "__testState", {
        value: state,
        configurable: false,
        writable: false
    });

    class TestRecognition {
        constructor() {
            this.continuous = true;
            this.lang = "en-US";
            this.interimResults = false;
            this.maxAlternatives = 1;
            this._isActive = false;
            window.recognition = this; // Store instance globally
        }

        start() {
            if (this._isActive) {
                return;
            }

            this._isActive = true;
            state.recognitionStartCalls += 1;

            const trigger = (callback) => {
                if (typeof callback === "function") {
                    try {
                        callback.call(this);
                    } catch (error) {
                        console.error("Test stub callback error", error);
                    }
                }
            };

            setTimeout(() => {
                trigger(this.onstart);
                trigger(this.onaudiostart);
                trigger(this.onspeechstart);
            }, 0);
        }

        stop() {
            if (!this._isActive) {
                return;
            }

            this._isActive = false;
            state.recognitionStopCalls += 1;

            const trigger = (callback) => {
                if (typeof callback === "function") {
                    try {
                        callback.call(this);
                    } catch (error) {
                        console.error("Test stub callback error", error);
                    }
                }
            };

            setTimeout(() => {
                trigger(this.onspeechend);
                trigger(this.onend);
            }, 0);
        }
    }

    window.SpeechRecognition = TestRecognition;
    window.webkitSpeechRecognition = TestRecognition;

    const synth = window.speechSynthesis;
    if (synth) {
        try {
            synth.getVoices = () => [];
        } catch (error) {
            console.warn("Unable to override getVoices", error);
        }

        try {
            Object.defineProperty(synth, "speaking", {
                configurable: true,
                get() {
                    return false;
                }
            });
        } catch (error) {
            console.warn("Unable to redefine speaking property", error);
        }

        const stubbedSpeak = (utterance) => {
            if (utterance.onstart) {
                utterance.onstart();
            }
            const spoken =
                typeof utterance === "string"
                    ? utterance
                    : typeof utterance?.text === "string"
                    ? utterance.text
                    : "";
            state.speakCalls.push(spoken);
            // Simulate onend event after a short delay
            setTimeout(() => {
                if (utterance.onend) {
                    utterance.onend();
                }
            }, 100);
        };

        try {
            synth.speak = stubbedSpeak;
        } catch (error) {
            try {
                Object.defineProperty(synth, "speak", {
                    configurable: true,
                    writable: true,
                    value: stubbedSpeak
                });
            } catch (defineError) {
                console.warn("Unable to override speechSynthesis.speak", defineError);
            }
        }

        try {
            synth.cancel = () => {};
        } catch (error) {
            console.warn("Unable to override speechSynthesis.cancel", error);
        }
    }

    if (!navigator.mediaDevices) {
        navigator.mediaDevices = {};
    }

    navigator.mediaDevices.getUserMedia = function () {
        state.getUserMediaCalls += 1;
        return Promise.resolve({
            getTracks() {
                return [
                    {
                        stop() {}
                    }
                ];
            }
        });
    };
})();
"""


@pytest.fixture
def loaded_page():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        page.add_init_script(STUB_SCRIPT)
        page.goto(SITE_URL, wait_until="domcontentloaded")
        page.wait_for_selector("#mute-indicator")
        yield page
        context.close()
        browser.close()

def test_speak_stops_and_restarts_recognition(loaded_page):
    page = loaded_page
    # Ensure recognition is active initially
    page.evaluate("window.__testState.recognitionStartCalls = 0")
    page.evaluate("window.__testState.recognitionStopCalls = 0")
    page.evaluate("isMuted = false") # Simulate unmuted mic
    page.wait_for_function("() => window.__testState.recognitionStartCalls > 0", timeout=10_000)

    # AI speaks, recognition should stop
    page.evaluate("speak('Hello')")
    page.wait_for_function("() => window.__testState.recognitionStopCalls > 0", timeout=10_000)
    stop_calls_after_speak = page.evaluate("() => window.__testState.recognitionStopCalls")
    assert stop_calls_after_speak > 0

    # AI finishes speaking, recognition should restart
    page.wait_for_function("() => window.__testState.recognitionStartCalls > 1", timeout=10_000)
    start_calls_after_speak_end = page.evaluate("() => window.__testState.recognitionStartCalls")
    assert start_calls_after_speak_end > 1
