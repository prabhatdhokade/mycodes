//Find the largest rectangular area possible in a given histogram 
//where the largest rectangle can be made of a number of contiguous bars.
// For simplicity, assume that all bars have same width and the width is 1 unit.
// input : 7
// 6 2 5 4 5 1 6
// output : 12
#include<bits/stdc++.h>

using namespace std ;
/*
int main() 
{ 
    int n ;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++) {
        cin>>arr[i];
    }

    stack <pair<int,int>> s;  // we'll store values in stack  in pair(first -> value, second -> index)
    vector < int > left;
    int psuedoIndex = -1; // just initialize for forther calc.

    for(int i = 0 ; i < n ; i++) {   // this entire loop will give us the LEFT smallest index
        if(s.size() == 0) {
            left.push_back(psuedoIndex);
        }

        else if ( s.size() > 0 && s.top().first < arr[i]) {
            left.push_back(s.top().second);
        }

        else if ( s.size() > 0 && s.top().first >= arr[i]) {
            while(s.size() > 0 && s.top().first >= arr[i]) {
                s.pop();
            }
            if ( s.size() == 0) {
                left.push_back(psuedoIndex);
            }
            else if (s.top().first < arr[i]) {
                left.push_back(s.top().second);
            }
        }
        s.push({arr[i],i}); 
    }   // output : -1 -1 1 1 3 -1 5
    
    while(!s.empty()) { // before moving we have to empty the stack
        s.pop();
    }

    vector < int > right;
    int psuedoIndex1 = n; // initialize for the right smaller index

    for(int i = n-1 ; i >=0 ; i--) {  //this entire loop will give us the RIGHT smallest index
        if(s.size() == 0) {
            right.push_back(psuedoIndex1);
        }

        else if ( s.size() > 0 && s.top().first < arr[i]) {
            right.push_back(s.top().second);
        }

        else if ( s.size() > 0 && s.top().first >= arr[i]) {
            while(s.size() > 0 && s.top().first >= arr[i]) {
                s.pop();
            }
            if ( s.size() == 0) {
                right.push_back(psuedoIndex1);
            }
            else if (s.top().first < arr[i]) {
                right.push_back(s.top().second);
            }
        }
        s.push({arr[i],i});
    }
    reverse(right.begin(), right.end());  // don't forget to reverse 
    //output :  1 5 3 5 5 7 7
    
    int width[n];
    for(int i =0; i < n ; i++){
        width[i] =  right[i] - left[i] - 1;  // this is IMP //
        //cout<< width[i] << " ";       // this gives us the width of each bar(index) 
    }
    
    int area[n]; // area will come from width * height
    for( int i =0 ; i < n; i++) {
        area[i] = width [i] * arr[i];
       // cout<< area[i] << " ";
    } 
    cout<< *max_element(area, area + n); // stl to print maximum element
    
  
} 
*/

int solve(int arr[],int n){
    int ans;
    vector<int> v1;
    stack<pair<int,int>> s;
    int j=0;
    while(j<n){
        if(s.size() == 0) v1.push_back(-1);
        else if(s.size() > 0 && s.top().first < arr[j]){
            v1.push_back(s.top().second);
        }  
        else if(s.size() > 0 && s.top().first >= arr[j]){
            while(s.size() > 0 && s.top().first >= arr[j]){
                s.pop();
            }
            if(s.size() == 0) v1.push_back(-1);
            else if(s.size() > 0 && s.top().first < arr[j]){
                v1.push_back(s.top().second);
            }
        }
        s.push({arr[j],j});
        j++;
    }

    while(s.size() > 0){
        s.pop();
    }
    vector<int> v2;
    int i = n-1;
    while(i >= 0){
        if(s.size() == 0) v2.push_back(n);
        else if(s.size() > 0 && s.top().first < arr[i]){
            v2.push_back(s.top().second);
        }
        else if( s.size() > 0 && s.top().first >= arr[i]){
            while(s.size() > 0 && s.top().first >= arr[i]){
                s.pop();
            }
            if(s.size() == 0) v2.push_back(n);
            else if(s.size() > 0 && s.top().first < arr[i]){
                v2.push_back(s.top().second);
            }
        }
        s.push({arr[i],i});
        i--;
    }
    reverse(v2.begin(),v2.end());
    int width[n];
    for(int i =0;i<n;i++){
        width[i] = v2[i] - v1[i] -1;
        //cout<< width[i]<<" ";
    }
    int area[n];
    for(int i=0;i<n;i++){
        area[i] = width[i] * arr[i];
    }

    return *max_element(area,area +n);
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    
    cout<<solve(arr,n);
    
} 