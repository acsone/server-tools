This module deactivates all bindings to openerp.com that
come with the standard code:

* update notifier code is deactivated and the function is overwritten
* apps and updates menu items in settings are hidden inside Tools\\Parameters
* help and account menu items in user menu are removed
* prevent lookup of OPW for current database uuid and resulting
  'unsupported' warning
