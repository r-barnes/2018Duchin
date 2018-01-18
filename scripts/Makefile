SOURCES = $(wildcard compactnesslib/*.cpp) $(wildcard compactnesslib/shapelib/*.cpp) $(wildcard compactnesslib/lib/*.cpp) main_network.cpp Timer.cpp compactnesslib/lib/spatialindex_c/spatialindex/Region.cpp compactnesslib/lib/spatialindex_c/rtree/RTree.cpp compactnesslib/lib/spatialindex_c/spatialindex/Point.cpp compactnesslib/lib/spatialindex_c/tools/Tools.cpp compactnesslib/lib/spatialindex_c/storagemanager/MemoryStorageManager.cpp compactnesslib/lib/spatialindex_c/spatialindex/LineSegment.cpp compactnesslib/lib/spatialindex_c/rtree/Leaf.cpp compactnesslib/lib/spatialindex_c/rtree/Node.cpp compactnesslib/lib/spatialindex_c/rtree/Statistics.cpp compactnesslib/lib/spatialindex_c/rtree/BulkLoader.cpp compactnesslib/lib/spatialindex_c/rtree/Index.cpp
OBJECTS = $(SOURCES:.cpp=.o)

CXX_FLAGS = -I compactnesslib/lib --std=c++11 -march=native -mtune=native -g -O3 -DNDEBUG -DDOCTEST_CONFIG_DISABLE -Wall -Wpedantic -DSIDX_DLL='' #-fsanitize=address
WARNINGS = -Wall -Wpedantic -pedantic -Wall -Wextra -Wcast-align -Wcast-qual -Wctor-dtor-privacy -Wdisabled-optimization -Wformat=2 -Winit-self -Wlogical-op -Wmissing-include-dirs -Wnoexcept -Wold-style-cast -Woverloaded-virtual -Wredundant-decls -Wshadow -Wsign-promo -Wstrict-null-sentinel -Wstrict-overflow=5 -Wswitch-default -Wundef
LIBS = -fopenmp

all: $(OBJECTS)
	$(CXX) $(CXX_FLAGS) $(WARNINGS) $(OBJECTS) -o net_compact.exe $(LIBS)

%.o: %.cpp
	$(CXX) $(CXX_FLAGS) $(WARNINGS) -c $< -o $@ $(LIBS)

clean:
	rm -rf compactness.exe compactnesslib/*.o compactnesslib/shapelib/*.o compactnesslib/lib/*.o *.o