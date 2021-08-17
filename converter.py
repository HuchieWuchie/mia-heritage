import argparse
import os
import numpy as np
import open3d as o3d

def makeDirIfNotExist(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def voxelize(fileIn, fileOut, bitDepth):
    pcd = o3d.io.read_point_cloud(fileIn)
    points = np.asarray(pcd.points)
    xDist = np.max(points[:,0]) - np.min(points[:,0])
    yDist = np.max(points[:,1]) - np.min(points[:,1])
    zDist = np.max(points[:,2]) - np.min(points[:,2])

    voxelGridSize = 2**bitDepth
    voxelSize = max(xDist, yDist, zDist) / voxelGridSize
    pcd = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxelSize)

    point_cloud_points = np.asarray([pt.grid_index for pt in pcd.get_voxels()])
    point_cloud_color = np.asarray([pt.color for pt in pcd.get_voxels()])

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud_points)
    pcd.colors = o3d.utility.Vector3dVector(point_cloud_color)
    #o3d.visualization.draw_geometries([pcd])
    o3d.io.write_point_cloud(fileOut, pcd, write_ascii=True)

    with open(fileOut) as temp:
        lines = temp.readlines()

    lines[4] = lines[4].replace('double', 'float')
    lines[5] = lines[5].replace('double', 'float')
    lines[6] = lines[6].replace('double', 'float')

    writer = open(fileOut,"w+")

    for line in lines:
        writer.write(line)

def convertASC(fileIn, outputFile):
    with open(fileIn) as f:
        lines = f.readlines()

    header = "ply\nformat ascii 1.0\nelement vertex " + str(len(lines)) + "\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n"
    fileOut = open(outputFile,"w+")
    fileOut.write(header)
    for line in lines:
        values = line.split('\n')[0].split(' ')[:6]
        line = ""
        for x in values:
            line += x + " "
        line += "\n"
        fileOut.write(line)

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, help='File or folder with files')
parser.add_argument('--voxel_bit_depth', type=int, help='Optional, voxelize point cloud to specified bit depth >0')
args = parser.parse_args()
stop = False

if not args.input:
    print("Missing --input")
    stop = True

if stop:
    exit()

filesIn = [args.input]
inputDir = os.path.dirname(filesIn[0])
outputDir = inputDir

if not os.path.isfile(args.input):
    if not os.path.isdir(args.input):
        print("ERROR: Input is neither a file or a folder")
        exit()

    _,_, filesIn = next(os.walk(args.input))

for file in filesIn:
    file = os.path.basename(file)
    ext = os.path.splitext(file)[-1]
    absFile = os.path.join(inputDir, file)
    fileOut = os.path.splitext(absFile)[0] + ".ply"

    print("Converting input file: ", absFile)
    print("To PLY output file: ", fileOut)

    if ext == ".asc":
        convertASC(absFile, fileOut)

    if args.voxel_bit_depth:
        print("Voxelizing with bit depth: ", args.voxel_bit_depth)
        voxelize(fileOut, fileOut, args.voxel_bit_depth)

    print("Done")
