from sklearn.linear_model import LinearRegression
from ReportWriter import *
from sketch_to_sheet import *

def get_facet_label(line_label, roof):
    for key, value in roof.facet_segment_ids.items():
        if line_label in value:
            return key

    return None

def get_facet_pitch(facet_label, df):
    for i, row in df.iterrows():
        if row["Face Label"] == facet_label:
            return row["Pitch"]

    return None

def get_line_type(line, df):
    for i, row in df.iterrows():
        if row["Line Label"] == line.id:
            return row["Type (R, H, V, K, E)"].upper()

    return None

def get_neighboring_flat_line(line, roof, df):
    ref_lines = []
    for key, value in roof.facet_segment_ids.items():
        if line.id in value:
            for label in value:
                ref_line = roof.get_line_by_id(label)

                if get_line_type(ref_line, df) in ["E", "R"]:
                    ref_lines.append(ref_line)

    return sorted(ref_lines, key=lambda ref_line: line.angle(ref_line))[-1]

def get_line_3d_length(line, pitch, angle):
    line_angle = np.arctan(pitch / 12) / abs(np.sin(np.radians(angle)))

    return line.drawing_length / line_angle

def get_actual_full_line_length(line_id, df):
    for i, row in df.iterrows():
        if row["Line Label"] == line_id:
            return float(row["Length (ft.)"])

    return None

def get_average_scale_factor(facet_id, roof, df):
    scale_factors = []
    for i, segment_id in enumerate(roof.facet_segment_ids[facet_id]):
        segment_length = roof.facet_segment_lengths[facet_id][i]

        _length = get_actual_full_line_length(segment_id, df)

        line = roof.get_line_by_id(segment_id)
        line_type = get_line_type(line, df)

        if line_type in ["E", "R"]:
            drawing_length = line.drawing_length
        else:
            pitch = get_facet_pitch(facet_id, df)
            ref_line = get_neighboring_flat_line(line, roof, df)
            angle = line.angle(ref_line)
            drawing_length = get_line_3d_length(line, pitch, angle)

        actual_length = _length * (segment_length / drawing_length)

        if _length == 0 or actual_length == 0:
            continue

        scale_factor = segment_length / actual_length

        scale_factors.append(scale_factor)

    return np.median(scale_factors)

def create_report(roof, fontsize):
    roof_line_map, pitch_area_map, face_count = process_datasheet(roof, fontsize, datasheet="res.csv")

    measurements = [
        sum(pitch_area_map.values()),
        face_count,
        '{0:,.0f}'.format(max(pitch_area_map, key=pitch_area_map.get)) + "/12",
        roof_line_map["R"],
        roof_line_map["H"],
        roof_line_map["V"],
        roof_line_map["K"],
        roof_line_map["E"],
        pitch_area_map
    ]

    writer = ReportWriter(
        roof.folder,
        ADDRESS,
        COMPANY,
        CONTACT,
        measurements
    )

    writer.create_report()
    return

def main(roof, manual=False):

    if not manual:
        df = pd.read_csv(os.path.join(roof.folder, "data_sheet.csv"))

        assert "-" not in list(df["Pitch"].values), "All pitch values must be given"

        value_counts = df["Length (ft.)"].value_counts()
        if "-" in value_counts:
            assert value_counts["-"] < df.shape[0] - 1, "At least 2 lengths must be given"

        X, Y = [], []
        for i, row in df.iterrows():
            if row["Length (ft.)"] != "-":
                line = roof.get_line_by_id(row["Line Label"])

                if row["Type (R, H, V, K, E)"].upper() in ["R", "E"]:
                    X.append(line.drawing_length)
                    Y.append(float(row["Length (ft.)"]))

                    ref_line = get_neighboring_flat_line(line, roof, df)
                    angle = line.angle(ref_line)

                    print(line.id, line.drawing_length)
                    print("\n")

                else: # Hips, Valleys, Rakes
                    # Find which facet this line is part of, adjust for pitch,
                    # then adjust for angle between an Eave/Ridge on facet

                    facet_label = get_facet_label(row["Line Label"], roof)
                    pitch = get_facet_pitch(facet_label, df)
                    ref_line = get_neighboring_flat_line(line, roof, df)
                    angle = line.angle(ref_line)

                    print(line.id, get_line_3d_length(line, pitch, angle))
                    print("\n")

                    X.append(get_line_3d_length(line, pitch, angle))
                    Y.append(float(row["Length (ft.)"]))

        X, Y = np.array(X).reshape(-1, 1), np.array(Y).reshape(-1, 1)
        reg = LinearRegression(fit_intercept=False).fit(X, Y)

        for i, row in df.iterrows():
            if row["Length (ft.)"] == "-":
                line = roof.get_line_by_id(row["Line Label"])

                if row["Type (R, H, V, K, E)"].upper() in ["R", "E"]:
                    x = np.array([line.drawing_length]).reshape(1, -1)

                    ref_line = get_neighboring_flat_line(line, roof, df)
                    angle = line.angle(ref_line)

                    print(line.id, line.drawing_length)
                    print("\n")

                    pred = int(reg.predict(x)[0][0])
                    if pred == 0:
                        pred = 1

                    df.iat[i, 2] = pred

                else: # Hips, Valleys, Rakes
                    # Find which facet this line is part of, adjust for pitch,
                    # then adjust for angle between an Eave/Ridge on facet

                    facet_label = get_facet_label(row["Line Label"], roof)
                    pitch = get_facet_pitch(facet_label, df)
                    ref_line = get_neighboring_flat_line(line, roof, df)
                    angle = line.angle(ref_line)

                    print(line.id, get_line_3d_length(line, pitch, angle))
                    print("\n")
                    x = np.array([get_line_3d_length(line, pitch, angle)]).reshape(1, -1)

                    pred = int(reg.predict(x)[0][0])
                    if pred == 0:
                        pred = 1

                    df.iat[i, 2] = pred

        for i, row in df.iterrows():
            if i >= len(roof.facets):
                break

            scale_factor = get_average_scale_factor(get_letter_id(i), roof, df)

            facet_label = get_facet_label(row["Line Label"], roof)

            pitch = get_facet_pitch(facet_label, df)

            roof_angle = np.arctan(pitch / 12)

            drawing_area = roof.facets[i].area

            area = int((drawing_area / np.cos(roof_angle)) / scale_factor**2)

            if area % 2 != 0:
                area += 1

            df.iat[i, 4] = area

        df.to_csv(os.path.join(roof.folder, "res.csv"), index=False)

    create_report(roof, roof.fontsize)

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--f", dest="folder")
    parser.add_argument("--s", dest="fontsize", default=8)
    parser.add_argument("--m", dest="manual", action="store_true")

    args = parser.parse_args()

    roof = Roof(args.folder, args.fontsize)

    main(roof, manual=args.manual)
