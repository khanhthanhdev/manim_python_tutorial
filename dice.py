# import tkinter as tk
import random

random.seed(8686868)


for i in range(10):
    first = random.randint(1,6)
    second = random.randint(1,6)
    third = random.randint(1,6)
    s = first + second + third

    if s >= 10:
        print(f"{first} {second} {third} => Tài")
    else:
        print(f"{first} {second} {third} => Xỉu")





# root = tk.Tk()
# root.title("Dice Roller")
# root.geometry("300x200")

# dice_faces = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']

# dice_label = tk.Label(root, font=("Helvetica", 200))
# result_label = tk.Label(root, font=("Helvetica", 50))

# def roll_dice():
#     first_die = random.randint(1,6)
#     second_die = random.randint(1,6)
#     third_die = random.randint(1,6)

#     dice_label.config(
#         text=f"{dice_faces[first_die-1]} {dice_faces[second_die-1]} {dice_faces[third_die-1]}"

#     )
#     dice_label.pack()

#     sum = first_die + second_die + third_die
#     result_label.config(text='Tài' if sum > 10 else 'Xỉu',
#                         foreground='red' if sum > 10 else 'green')
    
#     result_label.pack(after=dice_label)

# button_1 = tk.Button(root, text="Quay Xúc Xắc", command=roll_dice, foreground='blue')
# button_1.pack()

# root.mainloop()
