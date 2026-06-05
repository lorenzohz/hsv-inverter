import skimage as ski
from skimage import util
import sys
import numpy as np
import matplotlib.pyplot as plt

def gerar_circulo_cromatico(resolucao=400):
    '''
    Gera uma imagem sintética de um círculo cromático perfeito (RGB uint8).
    Isso serve como um mapa de referência visual para as cores.
    '''
    # Cria uma grade de coordenadas (X, Y)
    x = np.linspace(-1, 1, resolucao)
    y = np.linspace(1, -1, resolucao)
    xx, yy = np.meshgrid(x, y)

    # Converte as coordenadas cartesianas para polares (Raio e Ângulo)
    raio = np.sqrt(xx**2 + yy**2)
    angulo = np.arctan2(yy, xx)

    # O Ângulo vira o Matiz (Hue) normalizado de 0.0 a 1.0
    # O offset +0.25 rotaciona 90° para que hue=0 (vermelho) fique no topo
    hue = (angulo / (2 * np.pi) - 0.25) % 1.0
    
    # A Saturação cresce do centro para as bordas
    saturation = np.clip(raio, 0, 1)
    
    # O Valor (Brilho) é sempre 1.0 no círculo
    value = np.ones_like(raio)

    # Deixa o fundo branco onde o raio é maior que 1
    mascara_fundo = raio > 1.0
    saturation[mascara_fundo] = 0.0
    value[mascara_fundo] = 1.0

    # Monta e converte
    hsv_circulo = np.dstack((hue, saturation, value))
    rgb_circulo = ski.color.hsv2rgb(hsv_circulo)
    
    return util.img_as_ubyte(rgb_circulo)

def inversao_hsi(imagem, matiz, largura):
    '''
    Inverte uma faixa de valores de matiz em uma imagem no espaço de cores HSI.
    Retorna a imagem convertida em formato RGB (uint8).
    '''
    assert 0 <= matiz < 360, "Matiz deve estar entre 0 e 360 graus."
    assert 0 <= largura <= 180, "Largura deve estar entre 0 e 180 graus."

    hsi = ski.color.rgb2hsv(imagem)

    limite_inferior = (matiz - largura) / 360.0
    limite_superior = (matiz + largura) / 360.0

    hue = hsi[:, :, 0]

    if limite_inferior < 0.0:
        mascara = (hue >= (1.0 + limite_inferior)) | (hue <= limite_superior)
    elif limite_superior > 1.0:
        mascara = (hue >= limite_inferior) | (hue <= (limite_superior - 1.0))
    else:
        mascara = (hue >= limite_inferior) & (hue <= limite_superior)

    hue[mascara] = (hue[mascara] + 0.5) % 1.0 
    hsi[:, :, 0] = hue

    rgb_invertida = ski.color.hsv2rgb(hsi)
    return util.img_as_ubyte(rgb_invertida)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Forma de uso: python hsi_invert.py <input_image> <matiz> <largura>")
        sys.exit(1)

    imagem_path = sys.argv[1]
    try:
        matiz = float(sys.argv[2])
        largura = float(sys.argv[3])
    except:
        print('Matiz e Largura devem ser números.')
        sys.exit(1)

    # 1. Carrega a imagem do usuário e gera o círculo de referência
    try:
        img_original = ski.io.imread(imagem_path)
    except:
        print('Erro ao ler imagem. Verificar caminho.')
        sys.exit(1)
    circulo_original = gerar_circulo_cromatico()

    # 2. Aplica o algoritmo em AMBAS as imagens
    img_processada = inversao_hsi(img_original, matiz, largura)
    circulo_processado = inversao_hsi(circulo_original, matiz, largura)

    # 3. Salva apenas a imagem processada do usuário no disco
    ski.io.imsave("resultado.png", img_processada)
    print("Imagem do usuário processada e salva como 'resultado.png'!")

    # 4. Configura a exibição em uma grade 2x2
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    fig.suptitle(f'Filtro HSI: Centro em {matiz}°, Tolerância de ±{largura}°', fontsize=16)

    # Linha 1: Imagens do Usuário
    axes[0, 0].imshow(img_original)
    axes[0, 0].set_title('Imagem Original')
    axes[0, 0].axis('off')

    axes[0, 1].imshow(img_processada)
    axes[0, 1].set_title('Imagem Modificada')
    axes[0, 1].axis('off')

    # Linha 2: Círculos Cromáticos
    axes[1, 0].imshow(circulo_original)
    axes[1, 0].set_title('Círculo de Referência')
    axes[1, 0].axis('off')

    axes[1, 1].imshow(circulo_processado)
    axes[1, 1].set_title('Mapa da Modificação (Cores Invertidas)')
    axes[1, 1].axis('off')

    plt.tight_layout()
    plt.show()