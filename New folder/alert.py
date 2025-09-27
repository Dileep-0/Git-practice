import winsound

value = 105
for i in range(value):
    print(i)
    if i > 100:
        print("🚨 Alert: Value crossed 100!")
        winsound.Beep(2000, 10000)  # frequency, duration
        print("after")
