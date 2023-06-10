/*Given an unsorted array and two numbers x and k, find k closest values to x.
Input : arr[] = {10, 2, 14, 4, 7, 6}, x = 5, k = 3
output : 7 6 4 */

#include<bits/stdc++.h>

using namespace std;

int main() {
    int n;
    cin >> n ;
    int arr[n];
    for(int i = 0 ; i < n ; i++ ) { // Time complexity : nlogk
        cin >> arr[i];
    }
    int x;
    cin >> x;
    int k;
    cin >> k;

    priority_queue <pair <int,int> > maxh; // push the pair of the index and the key

    for ( int i =0 ; i < n ; i++ ) {
        maxh.push( {abs(arr[i] - x),arr[i] } ); // abs(arr[i] - x) -> gives us the closest differnce index
                    // this will sort according to the first value in pair 
        if ( maxh.size() > k) {
            maxh.pop();
        }
    }

    while ( maxh.size() > 0) {
        cout << maxh.top().second << " ";
        maxh.pop();
    }
}