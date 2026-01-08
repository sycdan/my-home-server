# Ensures /usr/sbin and /sbin are in PATH for non-interactive shells
if [[ ":$PATH:" != *":/usr/sbin:"* ]]; then
	export PATH="$PATH:/usr/sbin"
fi
if [[ ":$PATH:" != *":/sbin:"* ]]; then
	export PATH="$PATH:/sbin"
fi