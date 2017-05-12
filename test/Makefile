all: stl_vector stl_iostream

stl_vector: test_stl_vector.cpp
	cd .. && ./code-stylizer -v /usr/include/c++/6.3.1/vector -o vector.h
	mkdir -p out
	g++ -o out/test_stl_vector test_stl_vector.cpp
	out/test_stl_vector

stl_iostream: test_stl_iostream.cpp
	cd .. && ./code-stylizer -v /usr/include/c++/6.3.1/iostream -o iostream.h
	mkdir -p out
	g++ -o out/test_stl_iostream test_stl_iostream.cpp
	out/test_stl_iostream

clean:
	rm -rf out/