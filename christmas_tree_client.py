"""
    This module is responsible for handling the connection to the Christmas Tree.
"""

from threading import Thread
from typing import List, Dict, Any
import socket
import json
import struct
import time
import pathlib
import os
import random
from datetime import datetime


class ChristmasTreeClient(Thread):
    """
    This class is responsible for handling the connection to the Christmas Tree.
    """

    def __init__(self, client: socket.socket) -> None:
        super().__init__()
        self.__client = client

        max_color_count = 32
        max_step_count = 64

        self.__color_size = max_color_count * 3
        self.__step_size = max_step_count

        colors_format = "B" * self.__color_size
        steps_format = "B" * self.__step_size

        self.__struct_format = {
            "active": "H",
            "led_count": "H",
            "color_count": "H",
            "step_count": "H",
            "step_shift": "H",
            "color_shift": "H",
            "step_delay": "H",
            "led_interval": "H",
            "colors": colors_format,
            "steps": steps_format,
        }

        self.__struct_order = [
            "active",
            "led_count",
            "color_count",
            "step_count",
            "step_shift",
            "color_shift",
            "step_delay",
            "led_interval",
            "colors",
            "steps",
        ]

        self.__struct_format_str = "<" + (
            "".join([self.__struct_format[key] for key in self.__struct_order])
        )

        self.__start_on = (18, 0)
        self.__end_on = (23, 0)

        self.__config_path = pathlib.Path().resolve() / "configs"
        self.__current_configs_set: set[str] = set()
        self.__current_configs_list: list[str] = []
        self.__current_index = 0

    def __active_config(self) -> bytes:
        configs_list = list(os.listdir(self.__config_path))
        configs_set = set(configs_list)
        if self.__current_configs_set != configs_set:
            self.__current_configs_set = configs_set
            random.shuffle(configs_list)
            self.__current_configs_list = configs_list
            self.__current_index = 0
            print("reload")

        start_index = self.__current_index - 1
        while start_index != self.__current_index:
            try:
                self.__current_index = (self.__current_index + 1) % len(
                    self.__current_configs_list
                )
                config_file = (
                    self.__config_path
                    / self.__current_configs_list[self.__current_index]
                )
                print(f"Loading config file: {config_file}")
                file_data = self.__load_file(config_file)
                return self.__generate_struct(file_data)
            except (FileNotFoundError, json.JSONDecodeError, struct.error) as e:
                print(f"Error: {e}")
                continue
        raise FileNotFoundError("No valid config files found")

    def __load_file(self, file_path: pathlib.Path) -> Dict[str, Any]:
        """
        Load a file from the given path and return it as a dictionary.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run(self):
        """
        Start the thread that handles the connection to the Christmas Tree.
        """
        while True:
            try:
                now = datetime.now()
                if self.__start_on <= (now.hour, now.minute) < self.__end_on:
                    data = self.__active_config()
                else:
                    data = self.__generate_struct(
                        self.__load_file(self.__config_path / ".." / "config_off.json")
                    )

                self.__client.send(data)
                time.sleep(30)
            except (ConnectionResetError, ConnectionAbortedError) as e:
                print(f"Error: {e}")
                break
        self.__client.close()

    def __color_hex_to_rgb(self, color: str) -> tuple:
        """
        Recieve a color in hex format (e.g. "#FF00FF") and return it in RGB format (e.g. (255, 0, 255))

        Args:
            color (str): The color in hex format
        Returns:
            tuple: The color in RGB format
        """
        color = color.lstrip("#")
        return tuple(int(color[i : i + 2], 16) for i in (2, 0, 4))

    def __generate_struct(self, data: Dict[str, Any]) -> bytes:
        """
            Create a struct from the given data.
        Returns:
            bytes: The struct
        """
        struct_values = []
        colors = data.get("colors", [])
        color_count = len(colors)
        color_ints: List[int] = []
        for color_str in colors:
            color_ints.extend(self.__color_hex_to_rgb(color_str))
        color_ints.extend([0] * (self.__color_size - len(color_ints)))

        steps = list(data.get("steps", []))
        step_count = len(steps)
        steps.extend([0] * (self.__step_size - len(steps)))
        for key in self.__struct_order:
            if key == "active":
                struct_values.append(int(data.get("active", 0)))
            elif key == "color_count":
                struct_values.append(color_count)
            elif key == "step_count":
                struct_values.append(step_count)
            elif key == "colors":
                struct_values.extend(color_ints)
            elif key == "steps":
                struct_values.extend(steps)
            else:
                struct_values.append(data[key])

        return struct.pack(self.__struct_format_str, *struct_values)
