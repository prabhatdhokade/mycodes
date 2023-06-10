/* Given a list of points on the 2-D plane and an integer K. The task is to find K closest points to the origin and print them.

Note: The distance between two points on a plane is the Euclidean distance.

Example:
Input : point = [[3, 3], [5, -1], [-2, 4]], K = 2*/
#include<bits/stdc++.h>

using namespace std;

int main() {
    int n;
    cin >> n ;
    int arr[n][2];
    for(int i = 0 ; i < n ; i++ ) { 
        cin >> arr[i][2];
    }

    int k;
    cin >> k;


    priority_queue< pair<int,int >> maxh;

    for(int i =0 ; i < n ; i++) {
        maxh.push({arr[i][0] * arr[i][0] + arr[i][1] * arr[i][1] , { arr[i][0] , arr[i][1] } });
        // there is formula to calculate the distancee betnween two points 
        // distance = underroot of (x1-x2)^2 + (y1-y2)^2;

        if ( maxh.size() > k) {
            maxh.pop();
        }
    }

    while( maxh.size() > 0) {
        pair<int,int> p = maxh.top().second;
        cout<< p.first<< " " << p.second; 
    }

}