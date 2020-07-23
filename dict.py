import Metashape

QUALITY = {"Ultra":  Metashape.UltraQuality,
           "High":  Metashape.HighQuality,
           "Medium":  Metashape.MediumQuality,
           "Low":  Metashape.LowQuality,
           "Lowest": Metashape.LowestQuality}

ACCURACY = {"Highest": Metashape.HighestAccuracy,
            "High": Metashape.HighAccuracy,
            "Medium": Metashape.MediumAccuracy,
            "Low": Metashape.LowAccuracy,
            "Lowest": Metashape.LowestAccuracy}

FILTERING = {"No": Metashape.NoFiltering,
             "Mild": Metashape.MildFiltering,
             "Moderate": Metashape.ModerateFiltering,
             "Aggressive": Metashape.AggressiveFiltering}

POLYCOUNT = {"Low": Metashape.LowFaceCount,
             "Medium": Metashape.MediumFaceCount,
             "High": Metashape.HighFaceCount}

TARGETTYPE = {"12bit": Metashape.CircularTarget12bit,
              "14bit": Metashape.CircularTarget14bit,
              "16bit": Metashape.CircularTarget16bit,
              "20bit": Metashape.CircularTarget20bit,
              "Circular": Metashape.CircularTarget,
              "Cross": Metashape.CrossTarget}
