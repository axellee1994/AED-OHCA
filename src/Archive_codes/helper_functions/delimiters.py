import re

# sentence = "gate,swing_gate,lift_gate,bollard,entrance,fence,jersey_barrier,full-height_turnstile"

# formatted_sentence = sentence.replace(",", ", ")
# print(formatted_sentence)


# command = "ogr2ogr -f GPKG output.gpkg input.gpkg -t_srs EPSG:3414"
# command = "ogrinfo input.gpkg -so"
command = "ogr2ogr -f PostgreSQL PG:\"dbname=postgis user=yitong\" input.gpkg -nln table_name -lco GEOMETRY_NAME=geom -lco FID=id -nlt PROMOTE_TO_MULTI layer_name"

def split_command(command):
    splited = re.split(" ", command)

    result = ""

    for word in splited:
        # ignore if word is a \
        if word == "\\":
            continue
        elif ".gpkg" in word:
            result += word[:-5] + ", "
            continue
        elif "table_name" in word or "layer_name" in word:
            result += word + ", "
            continue

        result += "'" + word + "', "

    return result[:-2]

# print(split_command(command))