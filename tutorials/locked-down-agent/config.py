"""Settings for your Chalk environment. Edit these three values before running the steps."""

# The host of your Chalk API server. The Model Gateway is served from it, under /v1/router.
# Run `chalk config` and copy the host from the API Server row, without https://.
API_HOST = "api.chalk.ai"

# Your environment's ID. Run `chalk whoami` and copy the Env Id value.
ENVIRONMENT_ID = "your-environment-id"

# A chat model your Model Gateway serves that supports tool calling.
# Run `chalk router model list` to see the models available to you.
MODEL = "openai/gpt-4.1-mini"

# The Chalk secret that holds your Model Gateway API key (see "Before you start").
KEY_SECRET = "AGENT_GATEWAY_KEY"
