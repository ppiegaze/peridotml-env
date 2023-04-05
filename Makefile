NAME ?= esad
MAKEFILE_DIR := $(CURDIR)
SHELL := $(shell echo $$SHELL)

.PHONY: check-brew
check-brew:
	@if  ! which brew >/dev/null; then \
		/bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; \
		echo 'export PATH="/opt/homebrew/bin:$$PATH"' >> ~/.zshrc; \
		source ~/.zshrc; \
	fi

.PHONY: check-micromamba
check-micromamba:
	@$(SHELL) -i -c 'command -v micromamba > /dev/null || ( \
		echo "Micromamba not found. Installing..."; \
		if [ "$$(uname)" = "Darwin" ]; then \
			curl -L https://micro.mamba.pm/install.sh | bash; \
		else \
			curl -L https://micro.mamba.pm/install.sh | zsh; \
			source ~/.zshrc; \
		fi; \
	)'

.PHONY: create-env
create-env: check-micromamba
	@$(SHELL) -i -c '$${MAMBA_EXE} create -n $(NAME) -c conda-forge -y'
	@$(SHELL) -i -c '$${MAMBA_EXE} install -n $(NAME) -f $(MAKEFILE_DIR)/env.yaml -y && $${MAMBA_EXE} clean --all --yes'


.PHONY: install-spark
install-spark: check-brew
	brew install python3  # might be necessary
	brew install openjdk@11
	brew install apache-spark

	# Append the environment variables to ~/.zshrc
	echo 'export JAVA_HOME="$$(brew --prefix openjdk@11)"' >> ~/.zshrc
	echo 'export SPARK_HOME="$$(brew --prefix apache-spark)/libexec/"' >> ~/.zshrc
	echo 'export PATH="$$SPARK_HOME/bin:$$PATH"' >> ~/.zshrc

	source  ~/.zshrc


.PHONY: install-flyte
install-flyte:
	brew install flyteorg/homebrew-tap/flytectl


.PHONY: start-flyte-demo
start-flyte: install-flyte
	flytectl demo start


.PHONY: package
package:
	@$(SHELL) -i -c 'micromamba activate $(NAME) && pip install -e .\[dev\]'


.PHONY: install-pre-commit
	brew install pre-commit


.PHONY: install-p10k
install-p10k: check-brew
	brew install romkatv/powerlevel10k/powerlevel10k
	@echo -e "source $$(brew --prefix)/opt/powerlevel10k/powerlevel10k.zsh-theme" >>~/.zshrc
	@echo "[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh" >>~/.zshrc
	@$(SHELL) -i -c 'cp $(MAKEFILE_DIR)/configs/p10k.zsh ~/.p10k.zsh'
	source ~/.zshrc

.PHONY: help
help:
	@echo  '  check-brew            - Installs the brew package manager if it is not already installed'
	@echo  '  check-micromamba      - Installs target installs the micromamba package manager if it is not already installed`
	@echo  '  create-env            - Creates a new micromamba environment named NAME=[fill in], defaults to esad'
	@echo  '  install-spark          - Installs `spark` and required libraries'
	@echo  '  install-p10k          - Installs the powerlevel10k theme for Iterm2'