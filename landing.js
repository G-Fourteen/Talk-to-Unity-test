(() => {
    const dependencyLight = document.querySelector('[data-role="dependency-light"]');
    const dependencySummary = document.getElementById('dependency-summary');
    const launchButton = document.getElementById('launch-app');
    const statusMessage = document.getElementById('status-message');

    const LOOPBACK_HOST_PATTERN = /^(?:localhost|127(?:\.\d{1,3}){3}|::1|\[::1\])$/;

    const dependencyChecks = [
        {
            id: 'secure-context',
            label: 'Secure connection (HTTPS or localhost)',
            friendlyName: 'secure connection light',
            check: () =>
                Boolean(window.isSecureContext) || LOOPBACK_HOST_PATTERN.test(window.location.hostname)
        }
    ];

    let landingInitialized = false;

    function setStatusMessage(message, tone = 'info') {
        if (!statusMessage) {
            return;
        }

        statusMessage.textContent = message;
        if (message) {
            statusMessage.dataset.tone = tone;
        } else {
            delete statusMessage.dataset.tone;
        }
    }

    function evaluateDependencies() {
        const results = dependencyChecks.map((descriptor) => {
            let met = false;
            try {
                met = Boolean(descriptor.check());
            } catch (error) {
                console.error(`Dependency check failed for ${descriptor.id}:`, error);
            }

            return {
                ...descriptor,
                met
            };
        });

        const missing = results.filter((result) => !result.met);
        const allMet = missing.length === 0;

        updateDependencyUI(results, allMet);

        return { results, allMet, missing };
    }

    function updateDependencyUI(results, allMet) {
        if (dependencyLight) {
            dependencyLight.dataset.state = allMet ? 'pass' : 'fail';
            dependencyLight.setAttribute(
                'aria-label',
                allMet
                    ? 'All dependencies satisfied'
                    : 'Missing secure connection'
            );
        }

        if (dependencySummary) {
            if (allMet) {
                dependencySummary.textContent = 'Click the button below to start talking to Unity.';
            } else {
                dependencySummary.textContent = 'Please use a secure connection (HTTPS or localhost) to talk to Unity.';
            }
        }

        if (launchButton) {
            launchButton.href = allMet ? '/ai' : '#';
            if(!allMet) {
                launchButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    setStatusMessage('Please use a secure connection (HTTPS or localhost) to talk to Unity.', 'warning');
                });
            }
        }
    }

    function bootstrapLandingExperience() {
        if (landingInitialized) {
            return;
        }

        landingInitialized = true;

        evaluateDependencies();
    }

    document.addEventListener('DOMContentLoaded', bootstrapLandingExperience);

    if (document.readyState !== 'loading') {
        bootstrapLandingExperience();
    }
})();
