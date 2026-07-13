"""Safe model-gateway errors that never include credentials or raw responses."""


class ModelGatewayError(RuntimeError):
    """Base error for model integration boundaries."""


class ModelGatewayDisabledError(ModelGatewayError):
    """Raised when a disabled gateway is invoked."""


class ModelGatewayConfigurationError(ModelGatewayError):
    """Raised when enabled model configuration is incomplete."""


class ModelGatewayUnavailableError(ModelGatewayError):
    """Raised when the selected provider is not available."""


class ModelGatewayOutputError(ModelGatewayError):
    """Raised when a provider response cannot satisfy the output contract."""
