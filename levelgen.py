import random, sys

choices = ["P", " ", " ", " ", " "]

for i,a in enumerate(sys.argv):
    if i > 0: choices.append(a)
print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
for i in range(22):
    sys.stdout.write("P")
    for j in range(30):
        ch = random.choice(choices)
        sys.stdout.write(ch)
    sys.stdout.write("P\n")
print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
