from time import monotonic


def log_state(heat_pseudo_temp, current_temp, desired_temp=None, heat_state=None):
    desired_temp_str = '' if desired_temp is None else '{:.1f}'.format(desired_temp)
    heat_state = '\t' if heat_state is None else \
        '%.1f\t' % heat_pseudo_temp if heat_state else '\t%.1f' % heat_pseudo_temp
    line = '{:.2f}\t{:.1f}\t{}\t{}\n'.format(monotonic(), current_temp, desired_temp_str, heat_state)
    print(line.strip())
    try:
        with open('log.txt', 'a') as log:
            log.write(line)
    except OSError as e:
        pass
