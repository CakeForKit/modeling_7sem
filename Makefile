

.PHONY: uipy
uipy:
	pyuic5 ./mod7_2/ui/main_window.ui -o ui.py


.PHONY: clear
clear:
	find . -name "*:Zone.Identifier" -type f -delete