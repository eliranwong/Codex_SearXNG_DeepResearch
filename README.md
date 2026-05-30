# Codex SearXNG Deep Research & Web Search Skills

This repository contains custom [Codex](https://github.com/eliranwong/codex) skills designed to empower Codex with advanced web search and deep research capabilities using a local [SearXNG](https://github.com/searxng/searxng) instance.

It is the Codex counterpart to the Claude Code plugins in [Claude_SearXNG_DeepResearch](https://github.com/eliranwong/Claude_SearXNG_DeepResearch).

## Included Skills

- **`web-search`**: Perform category-specific and time-filtered queries via a local SearXNG engine.
- **`deep-research`**: A multi-phase research orchestrator that automatically runs queries, drills into subtopics, extracts full-text page content, and synthesizes cited research reports.

# Install SearXNG

Assuming you have Docker installed, run the following commands to install SearXNG:

> For Linux users, run:

```
mkdir -p ./searxng/core-config/
cd ./searxng/
curl -fsSL \
    -O https://raw.githubusercontent.com/searxng/searxng/master/container/docker-compose.yml \
    -O https://raw.githubusercontent.com/searxng/searxng/master/container/.env.example
cp -i .env.example .env
# edit the default port
sed -i 's/^#SEARXNG_PORT=8080/SEARXNG_PORT=4000/' .env
# edit API output format
sed -i 's/    - html/    - html\n    - json\n    - csv/' core-config/settings.yml
# start the service
docker compose up -d
```

> For macOS users, run:

```
mkdir -p ./searxng/core-config/
cd ./searxng/
curl -fsSL \
    -O https://raw.githubusercontent.com/searxng/searxng/master/container/docker-compose.yml \
    -O https://raw.githubusercontent.com/searxng/searxng/master/container/.env.example
cp -i .env.example .env
# edit the default port
sed -i '' 's/^#SEARXNG_PORT=8080/SEARXNG_PORT=4000/' .env
# edit API output format
sed -i '' 's/    - html/    - html\n    - json\n    - csv/' core-config/settings.yml
# start the service
docker compose up -d
```

**Remarks**: The installation scripts above changes the SearXNG default port from `8080` to `4000`. If you use another port, manually edit the files `web-search/SKILL.md` and `deep-research/SKILL.md` and change the port number 4000 to the one you use.

For more details, read https://docs.searxng.org/admin/installation-docker.html#installation-container

## Install Skill Files

Copy the two skill folders `web-search` and `deep-research` into either one of the following locations:

`~/.codex/skills/`

`~/agents/skills/`

Remarks: Be carefaul not to accidently delete the default system skills folder at `~/.codex/skills/.system`.

## Usage

For examples, enter in Codex CLI:

```
$web-search "Quantum Computing recent advances
```

Or:

```
$deep-research Quantum Computing recent advances
```

## Use Azure / Ollama Models in Codex CLI [Optional]

For example, edit the ~/.codex/config.toml file with:

```
model = "glm-5.1:cloud"
model_provider = "ollama-launch"
#model = "gpt-5.3-codex"
#model_provider = "azure"
model_reasoning_effort = "medium"

# Uncomment to use the five lines below at your own risk
#sandbox_mode = "danger-full-access"
#approval_policy = "never"
#web_search = "live"
#[sandbox_workspace_write]
#network_access = true

[profiles.ollama-launch]
openai_base_url = "http://127.0.0.1:11434/v1/"
model_provider = "ollama-launch"
forced_login_method = "api"

[model_providers.ollama-launch]
name = "Ollama"
base_url = "http://127.0.0.1:11434/v1/"
wire_api = "responses"

[model_providers.azure]
name = "Azure OpenAI"
base_url = "https://<resource-name>.openai.azure.com/openai/v1"
env_key = "AZURE_OPENAI_API_KEY"
wire_api = "responses"
```

### Export Environment Variables for Codex CLI

In case you want to use Azure / Ollama models in Codex CLI, you need to export the environment variables for Codex CLI:

```
export AZURE_OPENAI_API_KEY="your-key"
export OLLAMA_API_KEY="your-key"
```