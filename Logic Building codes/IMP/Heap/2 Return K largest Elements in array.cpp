/* write an efficient program for printing k largest elements in an array. Elements in array can be in any order.

For example, if given array is [1, 23, 12, 9, 30, 2, 50] and you are asked for the largest 3 elements i.e., k = 3 then your program should print 50, 30 and 23.
*/
/*  intput : 6
 20 4 10 3 7 15
 3
 output : 10 15 20 */
#include<bits/stdc++.h>

using namespace std;

int main() {
    int n;
    cin >> n ;
    int arr[n];
    for(int i = 0 ; i < n ; i++ ) {
        cin >> arr[i];
    }

    int  k;  // if there is something given like smallest,largest. k'th  or k elements then
    cin >> k; // definitely heap will use there 
            // for smaller -> maxheap
            // for greater -> minheap ( vice versa)
    priority_queue<int , vector <int> , greater<int>> minh; // minheap declairation

    for(int i = 0 ; i < n ; i++) { 
        minh.push(arr[i]);
        if (minh.size() > k ) {
            minh.pop();  // pop out the extra element
        }
    }

    while ( !minh.empty()) {
        cout << minh.top() << " ";
        minh.pop();
    }
    
}