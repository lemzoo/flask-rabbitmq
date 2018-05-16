from unittest.mock import Mock

import pytest

from broker.broker_rabbit.exceptions import (ExchangeNameDoesntMatch,
                                             ChannelDoesntExist,
                                             ExchangeNotDefinedYet)
from broker.broker_rabbit.rabbit import ExchangeHandler


@pytest.mark.unit_test
class TestExchangeHandler:
    def test_setup_exchange(self):
        channel = Mock()
        exchange_name = 'TEST_EXCHANGE_NAME'
        exchange_type = 'TEST_TYPE_EXCHANGE'
        durable = True
        auto_delete = False
        exchange_handler = ExchangeHandler(channel, exchange_name, exchange_type,
                                           durable, auto_delete)

        exchange_handler.setup_exchange()

        exchange_handler._channel.exchange_declare.assert_called_with(
            exchange=exchange_name, exchange_type=exchange_type, durable=durable, auto_delete=auto_delete)

    def test_setup_exchange_without_channel(self):
        exchange_handler = ExchangeHandler(None)

        with pytest.raises(ChannelDoesntExist):
            exchange_handler.setup_exchange()

    def test_setup_exchange_with_short_exchange_name(self):
        channel = Mock()
        exchange_name = '-'
        exchange_handler = ExchangeHandler(channel, exchange_name)

        with pytest.raises(ExchangeNameDoesntMatch):
            exchange_handler.setup_exchange()

    def test_get_exchange_name(self):
        exchange_name = 'TEST_EXCHANGE_NAME'
        exchange_handler = ExchangeHandler(None, exchange_name)

        ret = exchange_handler.get_exchange_name()
        assert ret == exchange_name

    def test_get_exchange_name_without_exchange(self):
        exchange_handler = ExchangeHandler(None, None)

        with pytest.raises(ExchangeNotDefinedYet):
            exchange_handler.get_exchange_name()
