# Authentication

`droid` authenticates through two mechanisms:

## Interactive Login (OAuth)

Run `droid` to start the interactive TUI. On first launch, it opens a browser window to log in via OAuth. This stores credentials in `~/.config/factory/` or similar.

## API Key (BYOK)

Factory supports Bring Your Own Key — set up API keys for your preferred providers:

1. Visit `factory.ai/settings/api-keys` or use the CLI:
   ```
   droid exec "Tell me my current provider config"
   ```

2. Supported providers: OpenAI, Anthropic, Google, Groq, Fireworks, DeepInfra, Hugging Face, Ollama, OpenRouter, Baseten

3. The BYOK free tier works immediately — no Factory subscription needed. Your tokens are drawn from your own API keys, not Factory's pool.

## Verifying Auth

```
# Should return a successful JSON response
droid exec -o json "Respond with: OK"
```

If this fails, you may need to run `droid` interactively once to complete the OAuth flow.
