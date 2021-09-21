import vsource.configs as configs

def face_attribute(face_path, max_interval=configs.max_interval, version='none'):
    if version == 'fsx':
        from vsource.algorithms.face_attribute_x import face_attribute_x
        return face_attribute_x(face_path, version='fsx-0.1', max_interval=max_interval)
    if version == 'cgy-2':
        from vsource.algorithms.face_attribute_x import face_attribute_y
        return face_attribute_y(face_path, version='cgy-2', max_interval=max_interval)
    from vsource.algorithms.face_attribute_x import face_attribute_z
    return face_attribute_z(face_path, version='cgy-1', max_interval=max_interval)