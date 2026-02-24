format:
	rg --files --hidden -g '*.py' --null | xargs -0 uv run black
