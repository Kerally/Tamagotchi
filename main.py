import sys
import os
import random
from save_manager import load_pet, save_pet
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
import time
from save_manager import SAVE_FILE

if os.name == "nt":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
console = Console(force_terminal=True, color_system="truecolor")


def clear():
    os.system("cls" if os.name == "nt" else "clear")

def status_rich(pet):
    console.clear()
    console.print(f"[bold]{pet.name}'s Status[/bold]\n")

    with Progress(
        TextColumn("{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("{task.completed}/100"),
        transient=False
    ) as progress:
        progress.add_task("Hunger   ", total=100, completed=pet.hunger)
        progress.add_task("Happiness", total=100, completed=pet.happiness)
        progress.add_task("Energy   ", total=100, completed=pet.energy)


def bar_with_rich(value):
    with Progress(
        TextColumn("{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("{task.completed}/100"),
        transient=True
    ) as progress:
        task = progress.add_task("Loading...", total=100)
        for i in range(101):
            progress.update(task, completed=i)
            time.sleep(0.01)  # имитация работы


class Pet:
    def __init__(self, name, hunger=None, happiness=None, energy=None,
                 last_feed=None, last_play=None, last_sleep=None):
        self.name = name
        self.hunger = hunger if hunger is not None else random.randint(0,50)
        self.happiness = happiness if happiness is not None else random.randint(0,50)
        self.energy = energy if energy is not None else random.randint(0,50)
        self.last_feed = last_feed if last_feed is not None else time.time()
        self.last_play = last_play if last_play is not None else time.time()
        self.last_sleep = last_sleep if last_sleep is not None else time.time()


    def decay_stats(self):
        """Падение параметров со временем: 1 очко за минуту"""
        now = time.time()
        # количество минут, прошедших с последнего обновления
        minutes_hunger = int((now - self.last_feed) / 30)
        minutes_happiness = int((now - self.last_play) / 30)
        minutes_energy = int((now - self.last_sleep) / 30)

        self.hunger = max(0, self.hunger - minutes_hunger)
        self.happiness = max(0, self.happiness - minutes_happiness)
        self.energy = max(0, self.energy - minutes_energy)

        # обновляем timestamps на текущий момент
        self.last_feed = now
        self.last_play = now
        self.last_sleep = now


    def feed(self):
        if self.hunger < 100:
            self.hunger = min(100, self.hunger + 25)
            self.last_feed = time.time()
            bar_with_rich(self.hunger)
            print(f"{self.name} ate!")
        else:
            print(f"{self.name} is not hungry.")


    def play(self):
        if self.happiness < 100:
            self.happiness = min(100, self.happiness + 20)
            self.last_play = time.time()
            bar_with_rich(self.happiness)
            print(f"{self.name} had fun!")
        else:
            print(f"{self.name} does not want to play.")


    def sleep(self):
        if self.energy < 100:
            self.energy = min(100, self.energy + 25)
            self.last_sleep = time.time()
            bar_with_rich(self.energy)
            print(f"{self.name} slept!")
        else:
            print(f"{self.name} is not tired.")


    def cheat_full_stats(self):
        self.hunger = 100
        self.happiness = 100
        self.energy = 100
        print("Cheat activated: All stats set to 100!")

    def cheat_zero_stats(self):
        self.hunger = 0
        self.happiness = 0
        self.energy = 0
        print("Cheat activated: All stats set to 0!")


    def to_dict(self):
        return {
            "name": self.name,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "last_feed": self.last_feed,
            "last_play": self.last_play,
            "last_sleep": self.last_sleep
        }


def main():
    saved_data = load_pet()
    if saved_data:
        pet = Pet(
            saved_data["name"],

            saved_data["hunger"],

            saved_data["happiness"],

            saved_data["energy"],

            saved_data["last_feed"],

            saved_data["last_play"],

            saved_data["last_sleep"]

        )
        # падение статов за время, пока программа была закрыта
        pet.decay_stats()
        print(f"Welcome back! {pet.name} has been loaded from save.")

    else:
        while True:
            pet_name = input("Enter your pet's name: ")
            if len(pet_name) > 10:
                print("Name of your pet has to be less than 10 symbols")
            else:
                break
        pet = Pet(pet_name)
        print(f"Welcome to the virtual pet game! You are now taking care of {pet.name}.")

    while True:
        status_rich(pet)
        try:
            action = int(input("\nWhat do you want to do? (1=feed, 2=play, 3=sleep, 0=exit, 222=reset): "))
            if action == 1:
                pet.feed()
            elif action == 2:
                pet.play()
            elif action == 3:
                pet.sleep()
            elif action == 0:
                save_pet(pet.to_dict())  # автосейв при выходе
                bar_with_rich(100)
                print("Game saved. Goodbye!")
                input("Press Enter to continue...")
                sys.exit()

            elif action == 999:  # чит на полные статы
                pet.cheat_full_stats()
            elif action == 111:  # чит на обнуление статов
                pet.cheat_zero_stats()
            elif action == 222:  # сброс прогресса
                confirm = input("Are you sure you want to delete the save and start a new pet? (y/n): ").lower()
                if confirm == "y":
                    if SAVE_FILE.exists():
                        SAVE_FILE.unlink()  # удаляет файл
                        print("Save deleted. You can now create a new pet.")
                    else:
                        print("No save file found. Starting a new pet anyway.")
                    input("Press Enter to continue...")
                    main()  # перезапуск игры с новым питомцем
                else:
                    print("Cancelled reset.")
            else:
                print("No such action.")

        except ValueError:
            print("Invalid input, you have to write a number: 1, 2 or 3.")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 