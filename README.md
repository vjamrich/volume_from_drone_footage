## Calculating volume of an object from drone's footage
This project aims to fully automate process of measuring volume of an object with complex geometry by using *photogrammetry*. Such automation eliminates a need for expensive heavy weight scales used at construction, excavation sites, and earth-moving operations in general.

By knowing volume of an object, its weight can be easily calculated (given its weight per cubic meter is known).

*What is photogrammetry?*
> Photogrammetry is the art, science, and technology of obtaining reliable information about physical objects and the environment through processes of recording, measuring, and interpreting photographic images and patterns of recorded radiant electromagnetic energy and other phenomena (Wolf and Dewitt, 2000; McGlone, 2004)

## Description
The code searches through predefined folder for drone footage and outputs volume of an object located between two markers. Additionally, user can adjust accuracy of an output by changing different parameters of a <code>config.json</code> file.
The code is meant to be set up to run at reoccurring intervals, where the drone will automatically capture and output it's footage into a single folder and the code will output volume of each captured object.

![](MeshGen_Visualization.gif)
*Reconstructing 3d mesh of an object based on drone's footage*
