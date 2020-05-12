from consts import *
from flask import Flask, jsonify
import threading

app = Flask(__name__)


def get_counted_value():
    return jsonify({
        'total': total,
        'out': ppl_out,
        'in': ppl_in
    })


@app.route('/get', methods=['GET'])
def get_counter():
    return get_counted_value()


def center(x, y, w, h):
    x1, y1 = w // 2, h // 2
    cx, cy = x + x1, y + y1
    return cx, cy  # Retorna o centro do retângulo


def make_offset_lines(frame):
    cv2.line(frame, (xy1[0], pos_line - offset), (xy2[0], pos_line - offset), CYAN)
    cv2.line(frame, (xy1[0], pos_line + offset), (xy2[0], pos_line + offset), CYAN)


def make_center_line(frame):
    cv2.line(frame, xy1, xy2, BLUE, 3)


def make_lines(frame):
    make_center_line(frame)
    make_offset_lines(frame)


def area_de_uma_pessoa(area):
    return int(area) > area_ret_min


def make_contours(x, y, largura, altura, frame, centro, i):
    cv2.putText(frame, str(i), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 2)
    cv2.circle(frame, centro, 4, RED, -1)
    cv2.rectangle(frame, (x, y), (x + largura, y + altura), GREEN, 2)


def infos_text(frame):
    cv2.putText(frame, f'TOTAL: {total}', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 2)
    cv2.putText(frame, f'OUT: {ppl_out}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE, 2)
    cv2.putText(frame, f'IN: {ppl_in}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED, 2)


def make_count(frame, closing):
    global total, ppl_out, ppl_in
    contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    i = 0
    for contour in contours:
        x, y, largura, altura = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        if area_de_uma_pessoa(area):
            centro = center(x, y, largura, altura)
            make_contours(x, y, largura, altura, frame, centro, i)
            if len(cache_detects) <= i:  # O cache ainda não tem a pessoa atual
                cache_detects.append([])  # Adiciona uma lista que irá guardar os dados dessa pessoa
            if pos_line - offset < centro[1] < pos_line + offset:
                cache_detects[i].append(centro)
            else:
                cache_detects[i].clear()
            i += 1

    if i == 0 or len(contours) == 0:
        cache_detects.clear()

    else:
        for detect in cache_detects:
            for (c, l) in enumerate(detect):
                if detect[c - 1][1] < pos_line < l[1]:  # Se subiu
                    detect.clear()
                    ppl_out += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, GREEN, 5)
                    continue
                if detect[c - 1][1] > pos_line > l[1]:  # Se desceu
                    detect.clear()
                    ppl_in += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, RED, 5)
                    continue
                if c > 0:
                    cv2.line(frame, detect[c - 1], l, RED, 1)
    infos_text(frame)


def show(dict_frames):
    make_lines(dict_frames['frame'])
    make_count(dict_frames['frame'], dict_frames['closing'])
    for key, value in dict_frames.items():
        cv2.imshow(key, value)


def logical_frame():
    bool, frame = cap.read()  # Pega a foto do video, que é o frame em sí, bool é um booleano que informa se o frame foi retornado
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # deixa o frame cinza
    except cv2.error:
        print('Vídeo encerrado!')
        exit(0)
    else:
        fgmask = fgbg.apply(gray)  # Faz a máscara do frame
        bool_val, threshold = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)  # Retorna a máscara "mais limpa"
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=2)
        dilatation = cv2.dilate(opening, kernel, iterations=8)
        closing = cv2.morphologyEx(dilatation, cv2.MORPH_CLOSE, kernel, iterations=8)  # Máscara final
        show({'frame': frame, 'closing': closing})


def run_cv_recogniser():
    while True:
        logical_frame()
        if cv2.waitKey(30) & 0xFF == ord('q'):  # Se a opção escolhida é para sair
            break  # Interrompe o loop


if __name__ == "__main__":
    th = threading.Thread(target=run_cv_recogniser, args=())
    th.start()
    app.run(debug=True, use_reloader=False)
    cap.release()
    cv2.destroyAllWindows()
