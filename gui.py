import argparse
from nicegui import ui, Client

# Custom
from gui.callbacks import GUIState
import gui.error_pages
# GPT
from lmm_utils.agent import Agent
import asyncio
agent=Agent(model_init=True)
@ui.page('/')
async def index(client: Client):
    global agent
    # Start the interface!
    gui_st = GUIState()
    gui_st.pattern_state.agent=agent
    # Connection end
    # https://github.com/zauberzeug/nicegui/discussions/1379

    await client.disconnected()

    print('Closed connection ', gui_st.pattern_state.id, '. Deleting files...')
    gui_st.release()

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        help='Host address to start the gui server ,defaults to "127.0.0.0"',
        type=str,
        default='0.0.0.0'
    )
    parser.add_argument(
        '--port',
        help='Use this port',
        type=str,
        default="8080"
    )
    args=parser.parse_args()
    ui.run(
            host=args.host,
            port=args.port,
            reload=False,
            favicon='assets/img/favicon.ico',
            title='Design2GarmentCode: Turning Design Concepts to Tangible Garments Through Program Synthesis'
        )