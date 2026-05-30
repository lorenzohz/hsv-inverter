import skimage as ski
from skimage import util  # 1. Importe o módulo util
import sys

def inversao_hsi(imagem, matiz, largura):
    '''
    Inverte uma faixa de valores de matiz em uma imagem no espaço de cores HSI.
    Parâmetros:
    - imagem: A imagem de entrada (em formato RGB).
    - matiz: O valor central da faixa de matiz a ser invertida (em graus, 0-360).
    - largura: A largura da faixa de matiz a ser invertida (em graus, 0-180).
    '''
    assert 0 <= matiz < 360, "Matiz deve estar entre 0 e 360 graus."
    assert 0 <= largura <= 180, "Largura deve estar entre 0 e 180 graus."

    # Converte a imagem para o espaço de cores HSI
    hsi = ski.color.rgb2hsv(imagem)

    # normaliza os parametros matiz para o intervalo [0, 1]
    limite_inferior = (matiz - largura) / 360.0
    limite_superior = (matiz + largura) / 360.0

    hue = hsi[:, :, 0]

    # Se o limite inferior for negativo, o pedaço faltante está no final do círculo (perto de 1.0)
    if limite_inferior < 0.0:
        mascara = (hue >= (1.0 + limite_inferior)) | (hue <= limite_superior)

    # Se o limite superior passar de 1.0, o pedaço extra recomeça no início (perto de 0.0)
    elif limite_superior > 1.0:
        mascara = (hue >= limite_inferior) | (hue <= (limite_superior - 1.0))

    # Caso normal (a faixa inteira está segura no meio de 0.0 a 1.0)
    else:
        mascara = (hue >= limite_inferior) & (hue <= limite_superior)

    # Inverte os valores de matiz que estão no range (matiz - largura, matiz + largura)
    hue[mascara] = (hue[mascara] + 0.5) % 1.0  # Inverte a matiz adicionando 180 graus (0.5 em escala [0, 1])
    hsi[:, :, 0] = hue

    # Converte de volta para RGB (Retorna um float64 entre 0 e 1)
    rgb_invertida = ski.color.hsv2rgb(hsi)

    # 2. Converte a imagem para inteiros de 8 bits (0 a 255)
    rgb_pronta_para_salvar = util.img_as_ubyte(rgb_invertida)

    # 3. Salva a imagem convertida
    ski.io.imsave("resultado.png", rgb_pronta_para_salvar)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Forma de uso: python hsi_invert.py <input_image> <matiz> <largura>")
        sys.exit(1)

    imagem = sys.argv[1]
    matiz = float(sys.argv[2])
    largura = float(sys.argv[3])

    img = ski.io.imread(imagem)

    inversao_hsi(img, matiz, largura)