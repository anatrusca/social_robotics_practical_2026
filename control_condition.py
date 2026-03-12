from autobahn.twisted.component import Component, run
from wow.game_runner import main_control as main


wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.69b276a4b788cadff345d775",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])