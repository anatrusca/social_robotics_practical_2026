from autobahn.twisted.component import Component, run
from wow.config import REALM, WAMP_URL
from wow.game_runner import build_main

wamp = Component(
    transports=[{
        "url": WAMP_URL,
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm=REALM,
)

wamp.on_join(build_main(condition="control"))

if __name__ == "__main__":
    run([wamp])