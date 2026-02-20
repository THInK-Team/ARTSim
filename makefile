UNAME_S := $(shell uname -s 2>NUL)

ifeq ($(UNAME_S),Linux)
	PYTHON := python3
else
	PYTHON := python
endif

# User inputs
model     ?= 
base_temp ?= 318.5

CONFIG := src/configure.py
MAIN   := ARTSim.py

# Detect flags (targets)
STEADY    := $(findstring steady_state,$(MAKECMDGOALS))
TRANSIENT := $(findstring transient,$(MAKECMDGOALS))

# Validation
ifeq ($(STEADY)$(TRANSIENT),)
$(error ERROR: You must specify at least one of steady_state or transient)
endif

# Default target
.PHONY: run steady_state transient

run:
	@echo Using Python: $(PYTHON)
	@echo Model: $(model)
	@echo baseTemp: $(base_temp)
	@echo Steady-state simulation enabled: $(if $(STEADY),YES,NO)
	@echo Transient simulation enabled: $(if $(TRANSIENT),YES,NO)

	$(PYTHON) $(CONFIG) \
		--model $(model) \
		--base-temp $(base_temp) \
		$(if $(STEADY),--steady-state,) \
		$(if $(TRANSIENT),--transient,)

	$(PYTHON) $(MAIN)

# Dummy phony targets for Makefile parsing
steady_state:
transient:
