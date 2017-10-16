SOURCES = $(wildcard compactnesslib/*.cpp) $(wildcard compactnesslib/shapelib/*.cpp) $(wildcard compactnesslib/lib/*.cpp) main_network.cpp Timer.cpp compactnesslib/lib/spatialindex_c/spatialindex/Region.cpp compactnesslib/lib/spatialindex_c/rtree/RTree.cpp compactnesslib/lib/spatialindex_c/spatialindex/Point.cpp compactnesslib/lib/spatialindex_c/tools/Tools.cpp compactnesslib/lib/spatialindex_c/storagemanager/MemoryStorageManager.cpp compactnesslib/lib/spatialindex_c/spatialindex/LineSegment.cpp compactnesslib/lib/spatialindex_c/rtree/Leaf.cpp compactnesslib/lib/spatialindex_c/rtree/Node.cpp compactnesslib/lib/spatialindex_c/rtree/Statistics.cpp compactnesslib/lib/spatialindex_c/rtree/BulkLoader.cpp compactnesslib/lib/spatialindex_c/rtree/Index.cpp
OBJECTS = $(SOURCES:.cpp=.o)

CXX_FLAGS = -I compactnesslib/lib --std=c++11 -march=native -mtune=native -g -O3 -DNDEBUG -DDOCTEST_CONFIG_DISABLE -Wall -Wpedantic -DSIDX_DLL='' #-fsanitize=address
LIBS = -fopenmp

all: $(OBJECTS)
	$(CXX) $(CXX_FLAGS) $(OBJECTS) -o net_compact.exe $(LIBS)

%.o: %.cpp
	$(CXX) $(CXX_FLAGS) -c $< -o $@ $(LIBS)

clean:
	rm -rf compactness.exe compactnesslib/*.o compactnesslib/shapelib/*.o compactnesslib/lib/*.o *.o