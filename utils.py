def cols_split(lines):
    #"split columns into lists, skipping blank and non-data lines"
    parsed = []
    for line in lines:
        raw_split = line.split()
        fields = [s for s in raw_split if (s and raw_split[0][0] == '#')]
        parsed.append(fields)
    return parsed
