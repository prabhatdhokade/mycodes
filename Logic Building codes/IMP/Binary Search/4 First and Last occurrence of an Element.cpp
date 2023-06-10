/* FIND FIRST AND LAST POSITIONS OF AN ELEMENT IN A SORTED ARRAY:

Given a sorted array with possibly duplicate elements,
 the task is to find indexes of first and last occurrences of an element x 
 in the given array.

Example:

Input : arr[] = {1, 3, 5, 5, 5, 5 ,67, 123, 125}    
        x = 5
Output : First Occurrence = 2
         Last Occurrence = 5 */
/*    
#include <bits/stdc++.h>
using namespace std;

int firstO(int arr[], int x, int n) { // for first occurrunce
    int start = 0;
    int in1 = -1;
    int end = n-1;

    while( start <= end) {
        int mid = start + (end - start) / 2; 

        if ( x == arr[mid] ) {
            in1 = mid;
            end = mid -1;
        }
        else if ( x < arr[mid]) {
            end  =mid - 1;
        }
        else 
            start  = mid + 1; 
    }
    return in1;
}

int lastO(int arr[], int x, int n ) { // for second occurunce
    int start = 0;
    int in1 = -1;
    int end = n-1;

    while( start <= end) {
        int mid = start + (end - start) / 2; 

        if ( x == arr[mid] ) {
            in1 = mid;
            start = mid + 1;
        }
        else if ( x < arr[mid]) {
            end  =mid - 1;
        }
        else 
            start  = mid + 1; 
    }
    return in1;
}

int main() {

    int n ;
    cin >> n;

    int arr[n];
    for(int i =0 ; i < n ; i++) {
        cin >> arr[i];
    }
    int ele;
    cin >> ele;

    int in1;
    int in2;

    in1 = firstO(arr, ele , n);
    in2 = lastO(arr,ele,n);

    cout<< in1 << " " << in2;
}
*/

#include<bits/stdc++.h>
using namespace std;

vector<int>solve(int arr[],int n,int k){
    vector<int>v;
    int first = -1;
    int last = -1;
    int start = 0;
    int end = n-1;
    while(start <= end){
        int mid = start + (end-start) /2;
        if(arr[mid] == k){
            first = mid;
            end = mid -1;
        }
        else if(arr[mid] < k){
            start = mid+1;
        }
        else if(arr[mid] > k){
            end = mid -1;
        }
    }
    start = 0;
    end = n-1;
    while(start <= end){
        int mid = start + (end-start) /2;
        if(arr[mid] == k){
            last = mid;
            start = mid +1;
        }
        else if(arr[mid] < k){
            start = mid+1;
        }
        else if(arr[mid] > k){
            end = mid -1;
        }
    }
    v.push_back(first);
    v.push_back(last);
    return v;
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
    vector<int>v;
    v = solve(arr,n,k);
    for(int i=0;i<v.size();i++){
        cout<<v[i]<<" ";
    }
}