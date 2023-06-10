/* Given a sorted array, find the element in the array which 
has minimum difference with the given number.
input : 5
       1 3 8 10 15
key   : 12
output : 10 :-minimum difference with number 12
*/


/*
#include <bits/stdc++.h>
using namespace std;

int main () {
    int n ;
    cin >> n;

    int arr[n];
    for(int i =0 ; i < n ; i++) {
        cin >> arr[i];
    }
    int  x;
    cin>> x;

    int start = 0;
    int end = n-1;
    int ans;

    while ( start <= end) { // please do dry run on paper u will get logic
        int mid = start + (end - start) /2;
        if ( arr[mid] == x ) { // if the given key is present then it will be of minimum diff(arr[mid] - key = 0)  and game over
            ans = arr[mid];
            break; 
        }
        else if ( arr[mid] > x ) { // bbut if the key is not present then we have to find the minimum diff between the smallest and greatest
            end = mid - 1;
        }
        else if ( arr[mid] < x) {
            start = mid + 1; 
        }
    }
    // if key isn't present in array, always the end becomes the floor and start becomes Ceil
    // but you don't put equations of floor and ceil,it happens automatically in while loop
    // just do dry run on paper u'll understand that.
    if ( abs(arr[end] - x) > abs(arr[start] - x)) { 
        cout << arr[start];
    }
    else if ( abs(arr[end] - x) <= abs(arr[start] - x) ){
        cout << arr[end];
    }

}

*/

#include<bits/stdc++.h>
using namespace std;

int solve(int arr[],int n,int k){
    int start =0;
    int end = n-1;
    while(start <= end){
        int mid = start + (end - start) /2;
        if(arr[mid] == k) return arr[mid];
        else if(arr[mid] > k) end = mid -1;
        else if(arr[mid] < k) start = mid +1;
    }
    // when u dont find the given number in the arr,then 'start' becomes the 'ceil' ans 'end' becomes the 'floor'
    if(abs(arr[end] - k) <= abs(arr[start] - k)) return arr[end];
    else
    return arr[start]; 
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    int k;
    cin>>k;
    cout<<solve(arr,n,k);
}



