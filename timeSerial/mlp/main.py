from mlp_class import mlp

red_mlp = None

while True:
    key = input("1. Crear una red para comprar\
        \n2. Crear una red para vender\
        \n3. Predecir precio (Necesaria una red)\
        \n4. Salir\n >> ")

    if key == '1':
        objeto = input("Selecciona el objeto que quieres predecir (Escribe el número):\
            \n\t- 19727\
            \n\t- 24325\
            \n\t- 24292\
            \n\t- 24344\
            \n\t- 24289\n")
        previos = input("Número par de objetos usados para predecir. Por defecto 10.\n")
        while int(previos)%2 != 0:
            previos = input("Te dije número par! >:( \n")

        iteraciones = input("Número de iteraciones para entrenar. Por defecto 100.\n")
        while int(iteraciones) <= 0:
            iteraciones = input("Pon un número grandote anda.\n")
        neuronas_ocultas = input("Número de neuronas ocultas. Por defecto 10.\n")
        while int(neuronas_ocultas) <= 0:
            neuronas_ocultas = input("Pon un número más mejor.\n")
        alpha = input("Ratio de aprendizaje. Por defecto 0.01.\n")
        while float(alpha) <= 0:
            alpha = input("Pon un número más mejor.\n")
        
        red_mlp = mlp('buy', objeto, int(previos), int(iteraciones), int(neuronas_ocultas), float(alpha))
        print(">>> Red entrenada! <<<\n")

    elif key == '2':
        objeto = input("Selecciona el objeto que quieres predecir (Escribe el número):\
            \n\t- 19727\
            \n\t- 24325\
            \n\t- 24292\
            \n\t- 24344\
            \n\t- 24289\n")
        previos = input("Número par de objetos usados para predecir. Por defecto 10.\n")
        while int(previos)%2 != 0:
            previos = input("Te dije número par! >:( \n")

        iteraciones = input("Número de iteraciones para entrenar. Por defecto 100.\n")
        while int(iteraciones) <= 0:
            iteraciones = input("Pon un número grandote anda.\n")
        neuronas_ocultas = input("Número de neuronas ocultas. Por defecto 10.\n")
        while int(neuronas_ocultas) <= 0:
            neuronas_ocultas = input("Pon un número más mejor.\n")
        alpha = input("Ratio de aprendizaje. Por defecto 0.01.\n")
        while float(alpha) <= 0:
            alpha = input("Pon un número más mejor.\n")

        red_mlp = mlp('sell', objeto, int(previos), int(iteraciones), int(neuronas_ocultas), float(alpha))

        print(">>> Red entrenada! <<<\n")

    elif key == '3':
        pasos = input("Introduce cuantos pasos de 2h quieres predecir\n")
        print("El proximo valor será %s" % red_mlp.predict(int(pasos)))

    elif key == '4':
        print("Bye bye!")
        exit()
    else:
        print("%s no, eso caca.\n" % key)

