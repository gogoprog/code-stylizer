#include <vector>
#include "../out/vector.h"

int main()
{
    Std::Vector<int, Std::Allocator<int>> myInts;

    myInts.pushBack(0);
    myInts.pushBack(1);
    myInts.pushBack(2);

    return 0;
}