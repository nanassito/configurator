# Configurator
A Python-based compiler for your configuration.

The goal of Configurator is to allow you to define templates and compile your configurations. That may sounds like templating but in practice it is quite different. Most notably, Configurator can:
* Run validation functions against a configuration before writting it out.
* Run a modifier to update a configuration before validating it.
* Merge multiple templates into a single configuration (composition instead of inheritance).
* Group configurations together and run modifiers and validations on all the configs together.

# Rationale
When running multiple similar application deployments, we often end up duplicating configurations. A classic solution to this is to use templating, however it has drawbacks, like for instance that it's often non-trivial to look at what the end configuration looks like. Another shortcoming of using templating is that there is no explicit validation, making it risky to modify the template.

Configurator aims to solve these problems by treating configuration like code: modifiers can be unit tested, tempaltes can be composed, and the output configurations can be validated programmatically.