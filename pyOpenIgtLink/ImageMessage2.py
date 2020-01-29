from pyOpenIgtLink import *
import enum
import numpy as np

IGTL_IMAGE_HEADER_VERSION = 1
IGTL_IMAGE_HEADER_SIZE = 72


class CoordSys(enum.IntEnum):
    """Coordinate system. Either left-posterior-superior (LPS) or right-anterior-superior (RAS)"""
    coordinateRas = 1,
    coordinateLps = 2


class Endian(enum.IntEnum):
    """Endian used in the bite array for the image data."""
    endianBig = 1,
    endianLittle = 2


class DataType(enum.IntEnum):
    """Data type either scalar or vector."""
    scalarType = 1,
    vectorType = 2


class PixelType(enum.IntEnum):
    """Pixel data type."""
    TYPE_INT8 = 2,
    TYPE_UINT8 = 3,
    TYPE_INT16 = 4,
    TYPE_UINT16 = 5,
    TYPE_INT32 = 6,
    TYPE_UINT32 = 7,
    TYPE_FLOAT32 = 10,
    TYPE_FLOAT64 = 11


s2np = {2: 'int8', 3: 'uint8', 4: 'int16', 5: 'uint16', 6: 'int32', 7: 'uint32', 10: 'float32', 11: 'float64'}
np2s = {v: k for k, v in s2np.items()}


class ImageMessage2(MessageBase):
    """
            Description for class
            The difference between ImageMessage2 and ImageMessage is related to the memory allocation, which is an issue
            in c++. In particular, ImageMessage2 in c++ allows to have the image raw data stored in a different (non
            contiguous) memory area wrt to the rest of the pack. That is, I can point to the image source data without
            the need to copy the image raw data in a memory area contiguous to the rest of the pack -> support for
            fragemnted packs. An issue in c++, in this python implementation ImageMessage and ImageMessage2 are the same

            :ivar _dimensions A vector containing the numbers of voxels in i, j and k directions.
            :ivar _spacing: A vector containing the spacings of the voxels in i, j and k directions.
            :ivar _SubDimensions  A vector containing the numbers of voxels of the subvolume in i, j and k directions.
            :ivar _subOffset  A vector containing the offset (number of voxels) of the first voxel of the subvolume
            from the first voxel of the original image.
            :ivar _matrix A matrix representing the origin and the orientation of the image.
            The matrix is set to identity by default
            :ivar _endian A variable for the Endian of the scalar values in the image.
            :ivar _numComponents A variable for the number of components
            :ivar _scalarType A variable for the scalar type of the voxels
            :ivar _coordinate A variable for the used coordinate system
            :ivar _imgHeader The binary image header
            :ivar _imgHeader The binary image data (raw data)
    """

    def __init__(self):
        MessageBase.__init__(self)

        # Setting image type
        self._messageType = "IMAGE"

        # Setting image header parameters
        self._dimensions = [0, 0, 0]
        self._spacing = [0, 0, 0]
        self._subDimensions = [0, 0, 0]
        self._subOffset = [0, 0, 0]
        self._matrix = np.identity(4)
        self._endian = Endian.endianBig
        self._numComponents = 1
        self._scalarType = PixelType.TYPE_UINT8
        self._coordinate = CoordSys.coordinateRas
        self._rawImage = np.array([0, 0])

    def setDimensions(self, dimensions):
        """ Sets image dimensions by an array of the numbers of pixels in i, j and k directions.
        SetDimensions() should be called prior to SetSubVolume(), since SetDimensions() sets subvolume
        parameters automatically assuming that subvolume = entire volume.
        :arg dimensions e-element list, tuple or array - rows, cols, channels

        """
        self._isBodyPacked = False
        self._dimensions[0] = dimensions[0]
        self._dimensions[1] = dimensions[1]
        self._dimensions[2] = dimensions[2]

        # Initialize subvolume
        self._subDimensions[0] = self._dimensions[0]
        self._subDimensions[1] = self._dimensions[1]
        self._subDimensions[2] = self._dimensions[2]
        self._subOffset[0] = 0
        self._subOffset[1] = 0
        self._subOffset[2] = 0

    def getDimensions(self):
        """Gets image dimensions as a tuple of the numbers of pixels in i, j and k directions.
        :return: number of pixels in i, j, k directions
        """
        return self._dimensions

    def setSubVolume(self, dims, off):
        """Sets sub-volume dimensions and offset by arrays of the dimensions and the offset.
        SetSubVolume() should be called after calling SetDiemensions(), since SetDimensions() reset the subvolume
        parameters automatically. Returns
        :param dims: 3-element list or array with the number of subvolume pixels in i, j, k directions
        :param off: 3-element list or array with the subvolume pixels offsets in i, j, k directions
        :return: True if the subvolume is successfully specified, False if an invalid subvolume is specified.
        """
        if off[0] + dims[0] >= self._dimensions[1] or off[1] + dims[1] >= self._dimensions[2] or \
            off[2] + dims[2] >= self._dimensions[2]:
            return False

        if off[0] < 0 or off[1] < 0 or off[2] < 0 or dims[0] < 0 or dims[1] < 0 or dims[2] < 0:
            return False

        self._isBodyPacked = False
        self._subDimensions[0], self._subDimensions[1], self._subDimensions[2] = dims[0], dims[1], dims[2]
        self._subOffset[0], self._subOffset[1], self._subOffset[2] = off[0], off[1], off[2]
        return True

    def getSubVolume(self):
        """Gets sub-volume dimensions and offset expressed in pixels in i, j, k directions

        :return: dims[3], off[3] - 2 lists containing dimensions and offsets of the subvolume
        """
        return self._subDimensions, self._subOffset

    def setSpacing(self, spacing):
        """Sets spacings by an array or list of spacing values in i, j and k directions.
        :param spacing: array or list of spacing values
        """
        self._isBodyPacked = False
        self._spacing = [float(spacing[i]) for i in range(3)]

    def getSpacing(self):
        """Gets spacings as an array or list of spacing values in i, j and k directions.
        :return list of spacing values
        """
        return self._spacing

    def setOrigin(self, origin):
        """ Sets the coordinates of the origin by an array of positions along the first (R or L),
        second (A or P) and the third (S) axes.
        :param: list or array with the origin coordinates
        """
        self._isBodyPacked = False
        self._matrix[1:3, 3] = np.array(origin)

    def getOrigin(self):
        """Gets the coordinates of the origin using an array of positions along the first (R or L),
        second (A or P) and the third (S) axes.

        :return: list of origin coordinates
        """
        return np.squeeze(self._matrix[1:3, 3])

    def setNormals(self, m):
        """Sets the orientation of the image by an array of the normal vectors for the i, j and k indexes.

        :param m: a 3x3 matrix containing the normal vectors stored in columns
        """
        self._isBodyPacked = False
        self._matrix[1:3, 1:3] = m

    def getNormals(self):
        """Gets the orientation of the image as an array of the normal vectors for the i, j and k indexes.

        :return: The image orientation vector concatenated in a matrix per columns
        """
        return self._matrix[1:3, 1:3]

    def setMatrix(self, matrix):
        """Sets the orientation and origin matrix.
        :param matrix: a 4x4 matrix representing the origin and the orientation of the image.
        """
        if not isinstance(matrix, type(np.array)) and matrix.shape != (4, 4):
            raise ValueError("Input must be a 4x4 matrix")

        self._matrix = matrix

    def getMatrix(self):
        """Gets the orientation and origin matrix.
        :return The 4x4 matrix representing the origin and the orientation of the image.
        """
        return self._matrix

    def setNumComponents(self, num):
        """Sets the number of components for each voxel.

        :param num: number of components for each voxel
        """
        if 0 < num < 255:
            self._numComponents = num

    def getNumComponents(self):
        """Gets the number of components for each voxel.

        :return: the number of components for each voxel.
        """
        return self._numComponents

    def setScalarType(self, stype):
        """Sets the image scalar type. (to one of PixelType)

        :param stype: image scalar type
        """
        self._scalarType = stype

    def setScalarTypeToInt8(self):
        """Sets the image scalar type to 8-bit integer.
        """
        self._scalarType = PixelType.TYPE_INT8

    def setScalarTypeToUint8(self):
        """Sets the image scalar type to 8-bit unsigned integer.
        """
        self._scalarType = PixelType.TYPE_UINT8

    def setScalarTypeToInt16(self):
        """Sets the image scalar type to 16-bit integer.
        """
        self._scalarType = PixelType.TYPE_INT16

    def setScalarTypeToUint16(self):
        """Sets the image scalar type to 16-bit unsigned integer.
        """
        self._scalarType = PixelType.TYPE_UINT16

    def setScalarTypeToInt32(self):
        """Sets the image scalar type to 32-bit integer.
        """
        self._scalarType = PixelType.TYPE_INT32

    def setScalarTypeToUint32(self):
        """Sets the image scalar type to 32-bit unsigned integer.
        """
        self._scalarType = PixelType.TYPE_UINT32

    def getScalarType(self):
        """Gets the image scalar type.

        :return the image scalar type
        """
        return np.dtype(s2np[self._scalarType])

    def getScalarSize(self):
        """Gets the size of the scalar type used in the current image data.

        :return The size of the scalar type used in the current image data. return ScalarSizeTable[scalarType];
        """
        return np.dtype(s2np[self._scalarType]).itemsize

    def setEndian(self, endian):
        """Sets the Endianess of the image scalars. (default is ENDIAN_BIG)
        :param endian Endianess of the image scalars
        """
        pass

    def getEndian(self, endian):
        """Gets the Endianess of the image scalars. (default is ENDIAN_BIG)
        :return The endianess of the image scalars
        """
        if not isinstance(endian, Endian):
            raise ValueError("input must be of type Endian")
        self._endian = endian

    def getImageSize(self):
        """
        Gets the size (length) of the byte array for the image data. The size is defined by
        dimensions[0]*dimensions[1]*dimensions[2]*scalarSize*numComponents.
        :return: The size of the byte array for the image data, expressed as
        dimensions[0]*dimensions[1]*dimensions[2]*scalarSize*numComponents.
        """
        return self._dimensions[0]*self._dimensions[1]*self._dimensions[2]*self.getScalarSize()*self._numComponents

    def setCoordinateSystem(self, coordSys):
        """Sets the coordinate system (COORDINATE_RAS or COORDINATE_LPS)
        :param coordSys The coordinate system (COORDINATE_RAS or COORDINATE_LPS)
        """
        if not isinstance(coordSys, CoordSys):
            raise ValueError("input must be of type CoordSys")
        self._coordinate = coordSys

    def getCoordinateSystem(self):
        """Gets the coordinate system (COORDINATE_RAS or COORDINATE_LPS)
        :return The coordinate system (COORDINATE_RAS or COORDINATE_LPS)
        """
        return self._coordinate

    def getSubVolumeSize(self):
        """Gets the size (length) of the byte array for the subvolume image data.
        The size is defined by subDimensions[0]*subDimensions[1]*subDimensions[2]*scalarSize*numComponents.
        :return The size (length) of the byte array for the subvolume image data.
        """
        self._subDimensions[0]*self._subDimensions[1]*self._subDimensions[2]*self.getScalarSize()*self._numComponents

    def setData(self, rawImgData):
        """
        Sets the image raw data
        :param rawImgData: image raw data
        :return True if the data were correctly set, False otherwise
        """
        if not isinstance(rawImgData, np.ndarray) or not 2 <= len(rawImgData.shape) <= 4:
            return False

        if len(rawImgData.shape) == 2:
            self._rawImage = np.expand_dims(rawImgData, axis = 2)
        else:
            self._rawImage = rawImgData

        imgShape = list(self._rawImage.shape)
        self.setDimensions(imgShape)

    def getData(self):
        """
        Gets the image raw data
        :return Rhe image raw data
        """
        return self._rawImage

    def _packContent(self, endian=">"):

        # IMAGE HEADER

        b_img_header = struct.pack(endian + 'HBBBB', IGTL_IMAGE_HEADER_VERSION, self._numComponents,
                                   self._scalarType, self._endian, self._coordinate)

        # Add the binarized dimension - number of pixels in each dimension
        for i in range(3):
            b_img_header += struct.pack(endian + 'H', self._dimensions[i])

        # Prepare the flatten transformation matrix and add its binarized version. The length of the axes must represent
        #  the pixel size (e.g. - spacing) in that dimension - therefore multiply it by the spacing
        matrix = np.zeros(12, dtype=np.float32)
        matrix[0:3] = self._matrix[0:3, 0] * self._spacing[0]
        matrix[3:6] = self._matrix[0:3, 1] * self._spacing[1]
        matrix[6:9] = self._matrix[0:3, 2] * self._spacing[2]
        matrix[9:12] = self._matrix[0:3, 3]  # Center position of the image (in millimeter)
        for i in range(12):
            b_img_header += struct.pack(endian + 'f', matrix[i])

        # Add the binarized subvolume offset
        for i in range(3):
            b_img_header += struct.pack(endian + 'H', self._subOffset[i])

        # Add the binarized subvolume dimension
        for i in range(3):
            b_img_header += struct.pack(endian + 'H', self._subDimensions[i])

        # IMAGE DATA
        self._rawImage = self._rawImage.astype(s2np[self._scalarType])  # convert the data to the correct format
        byte_order = "F" if self._endian == 2 else "C"
        b_data = self._rawImage.tostring(byte_order)

        # get binary message body = image header + image data
        self.body = b_img_header + b_data

        self._bodySize = len(self.body)

    def _unpackContent(self, endian = ">"):

        # unpack image header
        img_binary_header = self.body[0:IGTL_IMAGE_HEADER_SIZE]
        unpacked_header = struct.unpack(endian + 'HBBBBHHHffffffffffffHHHHHH', img_binary_header)

        # self._img_header_version = unpacked_header[0]
        self._numComponents = unpacked_header[1]
        self._scalarType = PixelType(unpacked_header[2])
        self._endian = Endian(unpacked_header[3])
        self._coordinate = CoordSys(unpacked_header[4])
        self._dimensions = list(unpacked_header[5:8])
        self._matrix[0:3, :] = np.reshape(np.array(unpacked_header[8:20]), [3, 4], order='F')
        self._subOffset = list(unpacked_header[20:23])
        self._subDimensions = list(unpacked_header[23:26])

        self._spacing = [0, 0, 0]
        self._spacing[0] = np.sqrt(self._matrix[0, 0] ** 2 + self._matrix[1, 0] ** 2 + self._matrix[2, 0] ** 2)
        self._spacing[1] = np.sqrt(self._matrix[0, 1] ** 2 + self._matrix[1, 1] ** 2 + self._matrix[2, 1] ** 2)
        self._spacing[2] = np.sqrt(self._matrix[0, 2] ** 2 + self._matrix[1, 2] ** 2 + self._matrix[2, 2] ** 2)

        self._matrix[0:3, 0] = self._matrix[0:3, 0] / self._spacing[0]
        self._matrix[0:3, 1] = self._matrix[0:3, 1] / self._spacing[1]
        self._matrix[0:3, 2] = self._matrix[0:3, 2] / self._spacing[2]

        # unpack image data
        img_data = self.body[IGTL_IMAGE_HEADER_SIZE::]
        flat_data = np.frombuffer(img_data, dtype=s2np[self._scalarType])

        self._rawImage = flat_data.reshape(self._dimensions)

    #not sure it is needed
    def _calculateContentSize(self):
        pass