from unittest.mock import Mock

import pytest

from broker_rabbit.exceptions import ChannelUndefinedError, ExchangeUndefinedError
from broker_rabbit.exchange_handler import ExchangeHandler


@pytest.mark.unit_test
class TestExchangeHandler:
    def test_raises_when_channel_is_not_defined(self):
        # Given
        channel = None
        exchange_name = 'TEST-EXCHANGE-NAME'

        # When
        exchange_handler = ExchangeHandler(channel, exchange_name)

        with pytest.raises(ChannelUndefinedError) as error:
            exchange_handler.setup_exchange()

        # Then
        assert 'The channel was not defined' == error.value.args[0]

    def test_should_setup_exchange_via_channel(self):
        # Given
        channel = Mock()
        exchange_name = 'TEST-EXCHANGE-NAME'
        exchange_handler = ExchangeHandler(channel, exchange_name)

        # When
        exchange_handler.setup_exchange()

        # Then
        channel.exchange_declare.assert_called_once_with(
            exchange=exchange_name, type='direct',
            durable=True, auto_delete=False)

    def test_raises_when_trying_to_get_exchange(self):
        # Given
        exchange_handler = ExchangeHandler(None, None)

        # When
        with pytest.raises(ExchangeUndefinedError) as error:
            exchange_handler.name

        # Then
        assert 'The exchange is not defined' == error.value.args[0]

    def test_get_exchange_name(self):
        # Given
        exchange_name = 'TEST-EXCHANGE-NAME'
        exchange_handler = ExchangeHandler(None, exchange_name)

        # When
        result = exchange_handler.name
        # Then
        assert exchange_name == result
