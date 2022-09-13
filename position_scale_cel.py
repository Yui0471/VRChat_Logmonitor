avatar_view_y = 0.55
position_x = -0.1546
position_y = 0.3570999
position_z = 0.4798998
scale = 1

def position_scale_calculation(viewposition_y):
    ratio = viewposition_y / avatar_view_y
    result_x = position_x * ratio
    result_y = position_y * ratio
    result_z = position_z * ratio
    result_s = scale * ratio
    return result_x, result_y, result_z, result_s

if __name__ == "__main__":
    result = position_scale_calculation(float(input("Y? :")))
    for f in result:
        print(f)
    input()
