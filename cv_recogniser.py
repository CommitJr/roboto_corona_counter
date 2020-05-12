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
    return x + w // 2, y + h // 2


def make_offset_lines(frame):
    cv2.line(frame, (xy1[0], pos_line - offset), (xy2[0], pos_line - offset), CYAN)
    cv2.line(frame, (xy1[0], pos_line + offset), (xy2[0], pos_line + offset), CYAN)


def make_center_line(frame):
    cv2.line(frame, xy1, xy2, BLUE, 3)


def make_lines(frame):
    make_center_line(frame)
    make_offset_lines(frame)


def people_common_area(area):
    return int(area) > area_ret_min


def two_people_rect(side):
    return int(side) < side_ret_max


def make_contours(x, y, sqr_width, sqr_height, frame, sqr_center, i):
    cv2.putText(frame, str(i), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 2)
    cv2.circle(frame, sqr_center, 4, RED, -1)
    cv2.rectangle(frame, (x, y), (x + sqr_width, y + sqr_height), GREEN, 2)


def infos_text(frame):
    cv2.putText(frame, f'TOTAL: {total}', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 2)
    cv2.putText(frame, f'OUT: {ppl_out}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE, 2)
    cv2.putText(frame, f'IN: {ppl_in}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED, 2)


def make_count(frame, closing):
    global total, ppl_out, ppl_in
    contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    i = 0
    for contour in contours:
        x, y, sqr_width, sqr_height = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        if people_common_area(area):
            sqr_center = center(x, y, sqr_width, sqr_height)
            make_contours(x, y, sqr_width, sqr_height, frame, sqr_center, i)
            if len(cache_detects) <= i:  # There's more people in the room
                cache_detects.append([])  # Creates a new slot in the list
            if pos_line - offset < sqr_center[1] < pos_line + offset:
                cache_detects[i].append(sqr_center)
            else:
                cache_detects[i].clear()
            i += 1

    if i == 0 or len(contours) == 0:
        cache_detects.clear()

    else:
        for detect in cache_detects:
            for (c, l) in enumerate(detect):
                if detect[c - 1][1] < pos_line < l[1]:  # Out
                    detect.clear()
                    ppl_out += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, GREEN, 5)
                elif detect[c - 1][1] > pos_line > l[1]:  # In
                    detect.clear()
                    ppl_in += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, RED, 5)
                elif c > 0:
                    cv2.line(frame, detect[c - 1], l, RED, 1)
    infos_text(frame)


def show(dict_frames):
    make_lines(dict_frames['frame'])
    make_count(dict_frames['frame'], dict_frames['closing'])
    for key, value in dict_frames.items():
        cv2.imshow(key, value)


def logical_frame():
    status, frame = cap.read()
    if not status:
        return status
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fgmask = fgbg.apply(gray)
    bool_val, threshold = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=2)
    dilatation = cv2.dilate(opening, kernel, iterations=8)
    closing = cv2.morphologyEx(dilatation, cv2.MORPH_CLOSE, kernel, iterations=8)
    show({'frame': frame, 'closing': closing})
    return True


def run_cv_recogniser():
    quit_process = lambda: cv2.waitKey(30) & 0xFF == ord('q')
    while True:
        status = logical_frame()
        if not status:
            break
        elif quit_process():
            break


if __name__ == "__main__":
    th = threading.Thread(target=run_cv_recogniser, args=())
    th.start()
    app.run(debug=True, use_reloader=False)
    cap.release()
    cv2.destroyAllWindows()
