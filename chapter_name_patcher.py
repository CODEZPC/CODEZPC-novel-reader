while True:
    for i in open(input("File Path:"),"r",encoding="utf-8").readlines():
        if i[0] != " ":
            open("RESULT","a",encoding="utf-8").write(i)