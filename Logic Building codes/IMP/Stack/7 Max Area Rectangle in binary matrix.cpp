/*Given a binary matrix, find the maximum size rectangle binary-sub-matrix with all 1’s.
Example:

Input :   0 1 1 0
          1 1 1 1
          1 1 1 1
          1 1 0 0

Output :  1 1 1 1 */
#include<bits/stdc++.h>

using namespace std;
/*
int MAH( vector<int> v, int n) 
{
    stack < pair<int , int >> s;
    vector < int > right;
    int psuedoIndex = n;

    for ( int i = n-1 ; i >= 0 ; i -- ) { // for nearest smaller to right 
        if ( s.size() == 0 ) {
            right.push_back(psuedoIndex);
        }
        else if ( s.size() > 0 && s.top().first < v[i] ) {
            right.push_back(s.top().second);
        }
        else if ( s.size() > 0 && s.top().first >= v[i] ) {
            while (s.size() > 0 && s.top().first >= v[i]) {
                s.pop();
            }
            if ( s.size() == 0 ) {
                right.push_back(psuedoIndex); // push the last index
            }
            else
                right.push_back(s.top().second);
        }
        s.push({v[i], i});
    }
    reverse(right.begin() , right.end());

    while ( !s.empty()) { // empty the stack for next filling
        s.pop();
    }

    vector < int > left;
    int psuedoIndex1 = -1;

    for ( int i = 0 ; i < n ; i++ ) { // for nearest smaller to left 
        if ( s.size() == 0 ) {
            left.push_back(psuedoIndex1);
        }
        else if ( s.size() > 0 && s.top().first < v[i] ) {
            left.push_back(s.top().second);
        }
        else if ( s.size() > 0 && s.top().first >= v[i] ) {
            while (s.size() > 0 && s.top().first >= v[i]) {
                s.pop();
            }
            if ( s.size() == 0 ) {
                left.push_back(psuedoIndex); // push the  -1 index
            }
            else
                left.push_back(s.top().second);
        }
        s.push({v[i], i});
    }

    vector<int> width;
    for(int i =0 ; i < n ; i++) {
        width[i] = right[i] - left[i] - 1;
    }
    int area[n] ; 
    for ( int i =0 ; i < n; i++) {
        area[i] = width[i] * v[i];
    }
    int x =*max_element( area , area + n);
    return x;
}


int main() 
{
    int n, m;
    cin>>n>>m;
    int arr[n][m];
    for ( int i =0; i < n; i++) {
        for ( int j =0; j < m; j++) {
            cin>>arr[i][j];
        }
    }
    for ( int i =0; i < n; i++) {
        for ( int j =0; j < m; j++) {
            cout<<arr[i][j]<<" ";
        }
    }

    vector < int > vec;

    for( int j= 0 ; j < m; j++) {
        vec.push_back(arr[0][j]) ;
        
    }
    for ( auto it= vec.begin() ; it!=vec.end(); it++) {
        cout<< *it << " ";
    }

   int mx = MAH(vec,n);
    
    for( int i =1 ; i < n ; i++ ) {
        for ( int j =0 ; j < m ; j++) {
            if ( arr[i][j] == 0 ) {
                vec[j] = 0;
            } 
            else 
                vec[j] = vec[j] + arr[i][j]; 
                
        }
        mx = max(mx, MAH(vec , n));
    }
    cout<< mx; 
}
*/

int MAH(vector<int>arr,int n){
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
    int m;
    cin>>n;
    cin>>m;
    int arr[n][m];
    for(int i=0;i<n;i++){
        for(int j=0;j<m;j++){
            cin>>arr[i][j];
        }
    }
    
    vector<int>v;
    for(int j=0;j<m;j++){
        v.push_back(arr[0][j]);
    }
    int mx = 0;
    mx = max(mx,MAH(v,m));

    for(int i=1;i<n;i++){
        for(int j=0;j<m;j++){
            if(arr[i][j] == 0){
                v[j] = 0;
            }
            else 
                v[j] = v[j] + arr[i][j];
        }
        mx = max(mx,MAH(v,m));
    }
    cout<< mx;

}
