from src import consts, controls
import cv2


def center(x, y, w, h):
    return x + w // 2, y + h // 2


def make_offset_lines(frame):
    cv2.line(frame, (consts.xy1[0], consts.pos_line - consts.offset), (consts.xy2[0], consts.pos_line - consts.offset),
             consts.CYAN)
    cv2.line(frame, (consts.xy1[0], consts.pos_line + consts.offset), (consts.xy2[0], consts.pos_line + consts.offset),
             consts.CYAN)


def make_center_line(frame):
    cv2.line(frame, consts.xy1, consts.xy2, consts.BLUE, 3)


def make_lines(frame):
    make_center_line(frame)
    make_offset_lines(frame)


def people_common_area(area):
    return int(area) > consts.area_ret_min


def two_people_rect(side):
    return int(side) < consts.side_ret_max


def make_contours(x, y, sqr_width, sqr_height, frame, sqr_center, i):
    cv2.putText(frame, str(i), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, consts.YELLOW, 2)
    cv2.circle(frame, sqr_center, 4, consts.RED, -1)
    cv2.rectangle(frame, (x, y), (x + sqr_width, y + sqr_height), consts.GREEN, 2)


def infos_text(frame):
    cv2.putText(frame, f'TOTAL: {consts.total}', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, consts.YELLOW, 2)
    cv2.putText(frame, f'OUT: {consts.ppl_out}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, consts.BLUE, 2)
    cv2.putText(frame, f'IN: {consts.ppl_in}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, consts.RED, 2)


def jump_on_x_detector(detect, c, l):
    return abs(detect[c - 1][0] - l[0]) > consts.jump_on_x_value


def make_count(frame, closing):
    contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    amount = []
    i = 0
    for contour in contours:
        x, y, sqr_width, sqr_height = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        if people_common_area(area):
            sqr_center = center(x, y, sqr_width, sqr_height)
            make_contours(x, y, sqr_width, sqr_height, frame, sqr_center, i)
            if len(amount) <= i:
                amount.append(1)
            if len(consts.cache_detects) <= i:  # There's more people in the room
                consts.cache_detects.append([])  # Creates a new slot in the list
            if consts.pos_line - consts.offset < sqr_center[1] < consts.pos_line + consts.offset:
                consts.cache_detects[i].append(sqr_center)
                amount[i] = 1 if sqr_width < consts.side_ret_max else 2
            else:
                consts.cache_detects[i].clear()
            i += 1

    if i == 0 or len(contours) == 0:
        consts.cache_detects.clear()

    else:
        i = 0
        for detect in consts.cache_detects:
            for (c, l) in enumerate(detect):
                if detect[c - 1][1] < consts.pos_line < l[1] and not jump_on_x_detector(detect, c, l):  # Out
                    detect.clear()
                    consts.ppl_out += amount[i]
                    consts.total = consts.total - amount[i] if consts.total >= amount[i] else 0
                    cv2.line(frame, consts.xy1, consts.xy2, consts.GREEN, 5)
                elif detect[c - 1][1] > consts.pos_line > l[1] and not jump_on_x_detector(detect, c, l):  # In
                    detect.clear()
                    consts.ppl_in += amount[i]
                    consts.total += amount[i]
                    cv2.line(frame, consts.xy1, consts.xy2, consts.RED, 5)
                elif c > 0:
                    cv2.line(frame, detect[c - 1], l, consts.RED, 1)
        i += 1
    infos_text(frame)


def show(dict_frames):
    make_lines(dict_frames['frame'])
    make_count(dict_frames['frame'], dict_frames['closing'])
    for key, value in dict_frames.items():
        cv2.imshow(key, value)


def logical_frame():
    status, frame = consts.cap.read()
    if not status:
        return False
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fgmask = consts.fgbg.apply(gray)
    bool_val, threshold = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=2)
    dilatation = cv2.dilate(opening, kernel, iterations=8)
    closing = cv2.morphologyEx(dilatation, cv2.MORPH_CLOSE, kernel, iterations=8)
    show({'frame': frame, 'closing': closing})
    return True


def run_cv_recogniser():
    controls.set_controls()
    quit_process = lambda: cv2.waitKey(30) & 0xFF == ord('q')
    while True:
        controls.update_controls_values()
        status = logical_frame()
        if not status:
            break
        elif quit_process():
            break
    consts.cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    run_cv_recogniser()
