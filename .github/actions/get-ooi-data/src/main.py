import datetime
import logging
import os
import sys

from ooipy.request import hydrophone_request

logging.basicConfig(
    format="%(levelname)s:%(message)s", stream=sys.stdout, level=logging.INFO
)

NODES = [
    "LJ01D",
    "LJ01A",
    "PC01A",
    "PC03A",
    "LJ01C",
    "LJ03A",
    "AXABA1",
    "AXCC1",
    "AXEC2",
    "HYS14",
    "HYSB1",
]

node = os.environ["INPUT_NODE"]
if node not in NODES:
    raise ValueError(f"Invalid node name {node}")

start_time = os.environ["INPUT_START_TIME"]
end_time = os.environ["INPUT_END_TIME"]

if end_time:
    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H-%M-%S")
else:
    end_time = datetime.datetime(year=2021, month=8, day=1, hour=6)

if start_time:
    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H-%M-%S")
else:
    start_time = datetime.datetime(year=2021, month=8, day=1, hour=0)

output_dir = os.environ["INPUT_OUTPUT_DIR"]
os.makedirs(output_dir, exist_ok=True)

segment_length = datetime.timedelta(minutes=float(os.environ["INPUT_SEGMENT_LENGTH"]))

while start_time < end_time:
    segment_end = min(start_time + segment_length, end_time)
    hydrophone_data = hydrophone_request.get_acoustic_data(
        start_time, segment_end, node, verbose=True
    )
    if hydrophone_data is None:
        logging.info(f"Could not get data from {start_time} to {segment_end}")
        start_time = segment_end
        continue
    datestr = start_time.strftime("%Y-%m-%dT%H-%M-%S-%f")[:-3]
    wav_name = f"{datestr}.wav"
    hydrophone_data.wav_write(os.path.join(output_dir, wav_name))
    start_time = segment_end
